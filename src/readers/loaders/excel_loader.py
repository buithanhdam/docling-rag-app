"""Pandas Excel reader.

Pandas parser for .xlsx files.

"""

import logging
import sys
from pathlib import Path
from typing import Any, List, Optional, Union

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from llama_index.core.readers.base import BaseReader

from src.readers.utils import split_text
from src.readers.base import Document

class PandasExcelReader(BaseReader):
    r"""Pandas-based CSV parser.

    Parses CSVs using the separator detection from Pandas `read_csv` function.
    If special parameters are required, use the `pandas_config` dict.

    Args:

        pandas_config (dict): Options for the `pandas.read_excel` function call.
            Refer to https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html
            for more information. Set to empty dict by default,
            this means defaults will be used.

    """

    def __init__(
        self,
        *args: Any,
        pandas_config: Optional[dict] = None,
        row_joiner: str = "\n",
        col_joiner: str = " ",
        **kwargs: Any,
    ) -> None:
        """Init params."""
        super().__init__(*args, **kwargs)
        self._pandas_config = pandas_config or {}
        self._row_joiner = row_joiner if row_joiner else "\n"
        self._col_joiner = col_joiner if col_joiner else " "

    def load_data(
        self,
        file: Path,
        include_sheetname: bool = False,
        sheet_name: Optional[Union[str, int, list]] = None,
        extra_info: Optional[dict] = None,
        **kwargs,
    ) -> List[Document]:
        """Parse file and extract values from a specific column.

        Args:
            file (Path): The path to the Excel file to read.
            include_sheetname (bool): Whether to include the sheet name in the output.
            sheet_name (Union[str, int, None]): The specific sheet to read from,
                default is None which reads all sheets.

        Returns:
            List[Document]: A list of`Document objects containing the
                values from the specified column in the Excel file.
        """
        import itertools

        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "install pandas using `pip3 install pandas` to use this loader"
            )

        if sheet_name is not None:
            sheet_name = (
                [sheet_name] if not isinstance(sheet_name, list) else sheet_name
            )

        dfs = pd.read_excel(file, sheet_name=sheet_name, **self._pandas_config)
        sheet_names = dfs.keys()
        df_sheets = []

        for key in sheet_names:
            sheet = []
            if include_sheetname:
                sheet.append([key])
            dfs[key] = dfs[key].dropna(axis=0, how="all")
            dfs[key] = dfs[key].dropna(axis=0, how="all")
            dfs[key].fillna("", inplace=True)
            sheet.extend(dfs[key].values.astype(str).tolist())
            df_sheets.append(sheet)

        text_list = list(
            itertools.chain.from_iterable(df_sheets)
        )  # flatten list of lists

        output = [
            Document(
                text=self._row_joiner.join(
                    self._col_joiner.join(sublist) for sublist in text_list
                ),
                metadata=extra_info or {},
            )
        ]

        return output


class ExcelReader(BaseReader):
    r"""Spreadsheet exporter respecting multiple worksheets

    Parses CSVs using the separator detection from Pandas `read_csv` function.
    If special parameters are required, use the `pandas_config` dict.

    Args:

        pandas_config (dict): Options for the `pandas.read_excel` function call.
            Refer to https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html
            for more information. Set to empty dict by default,
            this means defaults will be used.

    """

    def __init__(
        self,
        *args: Any,
        pandas_config: Optional[dict] = None,
        row_joiner: str = "\n",
        col_joiner: str = " ",
        rows_per_doc: int = 1,
        max_words_per_page:int=2048,
        **kwargs: Any,
    ) -> None:
        """Init params."""
        super().__init__(*args, **kwargs)
        self._pandas_config = pandas_config or {}
        self._row_joiner = row_joiner if row_joiner else "\n"
        self._col_joiner = col_joiner if col_joiner else " "
        self._rows_per_doc = rows_per_doc
        self.max_words_per_page = max_words_per_page

    def load_data(
        self,
        file: Path,
        include_sheetname: bool = True,
        sheet_name: Optional[Union[str, int, list]] = None,
        extra_info: Optional[dict] = None,
        **kwargs,
    ) -> List[Document]:
        """Parse file and extract values from a specific column.

        Args:
            file (Path): The path to the Excel file to read.
            include_sheetname (bool): Whether to include the sheet name in the output.
            sheet_name (Union[str, int, None]): The specific sheet to read from,
                default is None which reads all sheets.

        Returns:
            List[Document]: A list of`Document objects containing the
                values from the specified column in the Excel file.
        """

        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "install pandas using `pip3 install pandas` to use this loader"
            )

        if sheet_name is not None:
            sheet_name = (
                [sheet_name] if not isinstance(sheet_name, list) else sheet_name
            )

        # clean up input
        file = Path(file)
        extra_info = extra_info or {}

        dfs = pd.read_excel(file, sheet_name=sheet_name, **self._pandas_config)
        # Nếu chỉ có một sheet, chuyển đổi sang dạng dictionary
        if isinstance(dfs, pd.DataFrame):
            dfs = {sheet_name[0]: dfs}

        output = []

        # Lặp qua từng sheet trong file Excel
        for idx, key in enumerate(dfs.keys()):
            df = dfs[key]
            df = df.dropna(axis=0, how="all").astype("object")
            df.fillna("", inplace=True)

            rows = df.values.astype(str).tolist()

            for i in range(0, len(rows), self._rows_per_doc):
                batch_rows = rows[i:i + self._rows_per_doc]
                
                # Kết hợp các hàng và cột thành chuỗi
                content = self._row_joiner.join(
                    self._col_joiner.join(row).strip() for row in batch_rows
                ).strip()
                contents=split_text(content,max_tokens=self.max_words_per_page)
                for c_i,c in enumerate(contents):
                    if include_sheetname:
                        c = f"(Sheet {key} of file {file.name})\n{c}"
                    
                    metadata = {
                        "page_label": idx + 1,
                        "sheet_name": key,
                        "batch_start_row": i + 1,
                        "batch_end_row": i + len(batch_rows),
                        "content_index":c_i+1,
                        **extra_info
                    }
                    output.append(Document(text=c, metadata=metadata))
        return output