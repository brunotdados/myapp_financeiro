from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class ConsolidationResult:
    output_path: Path
    rows: int
    columns: list[str]


class NubankCsvService:
    BANK_NAMES = {
        "bruno": "nubank bruno",
        "mayara": "nubank mayara",
    }

    COLUMN_NAMES = {
        "date": "data_compra",
        "title": "descricao",
        "amount": "valor",
    }
    CATEGORY_COLUMNS = ["categoria", "subcategoria"]
    CATEGORY_MERGE_KEYS = [
        "data_compra",
        "descricao",
        "valor",
        "origem",
        "NUMANOMES",
        "banco",
    ]

    def consolidate_files(
        self,
        files_by_account: dict[str, list[Path]],
        output_path: Path,
    ) -> ConsolidationResult:
        frames: list[pd.DataFrame] = []

        for account_name, files in files_by_account.items():
            account_frames = [
                self._read_nubank_csv(file_path) for file_path in sorted(files)
            ]
            if not account_frames:
                continue

            account_df = pd.concat(account_frames, ignore_index=True)
            account_df["banco"] = self.BANK_NAMES.get(account_name, account_name)
            frames.append(account_df)

        if not frames:
            raise ValueError("Nenhum CSV do Nubank foi encontrado para consolidar.")

        final_df = pd.concat(frames, ignore_index=True)
        final_df = final_df[final_df["amount"] >= 0]
        final_df = final_df.rename(columns=self.COLUMN_NAMES)
        final_df = self._preserve_existing_categories(final_df, output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        final_df.to_csv(output_path, index=False, decimal=".", sep=",")

        return ConsolidationResult(
            output_path=output_path,
            rows=len(final_df),
            columns=list(final_df.columns),
        )

    def _read_nubank_csv(self, file_path: Path) -> pd.DataFrame:
        df = pd.read_csv(file_path, sep=",")
        file_name = file_path.name
        df["origem"] = file_name
        df["NUMANOMES"] = self._extract_year_month(file_name)
        return df

    @staticmethod
    def _extract_year_month(file_name: str) -> str:
        if file_name.startswith("Nubank_") and len(file_name) >= 14:
            return file_name[7:14].replace("-", "")
        return "Desconhecido"

    def _preserve_existing_categories(
        self,
        new_df: pd.DataFrame,
        output_path: Path,
    ) -> pd.DataFrame:
        for column in self.CATEGORY_COLUMNS:
            if column not in new_df.columns:
                new_df[column] = ""

        if not output_path.exists():
            return new_df

        existing_df = pd.read_csv(output_path)
        if not all(column in existing_df.columns for column in self.CATEGORY_COLUMNS):
            return new_df

        if not all(column in existing_df.columns for column in self.CATEGORY_MERGE_KEYS):
            return new_df

        new_with_key = self._add_occurrence_key(new_df)
        existing_with_key = self._add_occurrence_key(existing_df)

        category_lookup = existing_with_key[
            self.CATEGORY_MERGE_KEYS + ["_occurrence"] + self.CATEGORY_COLUMNS
        ]
        merged_df = new_with_key.drop(columns=self.CATEGORY_COLUMNS).merge(
            category_lookup,
            on=self.CATEGORY_MERGE_KEYS + ["_occurrence"],
            how="left",
        )
        merged_df = merged_df.drop(columns=["_occurrence"])

        for column in self.CATEGORY_COLUMNS:
            merged_df[column] = merged_df[column].fillna("").astype(str)

        return merged_df

    def _add_occurrence_key(self, df: pd.DataFrame) -> pd.DataFrame:
        keyed_df = df.copy()
        keyed_df["NUMANOMES"] = keyed_df["NUMANOMES"].astype(str)
        keyed_df["_occurrence"] = keyed_df.groupby(
            self.CATEGORY_MERGE_KEYS,
            dropna=False,
        ).cumcount()
        return keyed_df
