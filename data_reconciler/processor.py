from typing import List, Dict, Any
import pandas as pd

class DataReconciler:
    @staticmethod
    def get_discrepancies(source_df: pd.DataFrame, target_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
            Compute list of fields in records from two similar datasets 
            with discrepancies 
        """
        
        discrepancies = []
        common_idx = source_df.index.intersection(target_df.index)
        for idx in common_idx:
            src_row = source_df.loc[idx]
            tgt_row = target_df.loc[idx]
            diff = {}
            for col in source_df.columns:
                src_val = src_row[col]
                tgt_val = tgt_row[col]
                if pd.isnull(src_val) and pd.isnull(tgt_val):
                    continue
                if src_val != tgt_val:
                    diff[col] = {"source": src_val, "target": tgt_val}
            if diff:
                discrepancies.append({
                    "key": idx if isinstance(idx, tuple) else (idx, ),
                    "original_records": {
                        "source": source_df.loc[idx].to_dict(),
                        "target": target_df.loc[idx].to_dict()
                    },
                    "differences": diff

                })
        return discrepancies
    
    @classmethod
    def reconcile(
        cls,
        source_data: List[Dict[str, Any]],
        target_data: List[Dict[str, Any]],
        unique_fields: List[str]
    ) -> Dict[str, Any]:
        """
        Core reconciliation logic:
        - Finds records present in source but missing in target.
        - Finds records present in target but missing in source.
        - Finds records present in both but with discrepancies.
        """

        if source_data == []:
            return ValueError("Source dataset cannot be empty")
        if target_data == []:
            return ValueError("Target dataset cannot be empty")
        if unique_fields == []:
            return ValueError("Unique fields cannot be empty")

        # Convert data to pandas' dataframe and set index for easy comparison
        source_df = pd.DataFrame(source_data)
        target_df = pd.DataFrame(target_data)
        source_df.set_index(unique_fields, inplace=True)
        target_df.set_index(unique_fields, inplace=True)

        if source_df.equals(target_df):
            return {
                "missing_in_source": [],
                "missing_in_target": [],
                "discrepancies": []
            }

        missing_in_target = source_df.loc[
            ~source_df.index.isin(target_df.index)
        ].reset_index().to_dict(orient='records')

        missing_in_source = target_df.loc[
            ~target_df.index.isin(source_df.index)
        ].reset_index().to_dict(orient='records')

        discrepancies = cls.get_discrepancies(source_df, target_df)

        return {
            "missing_in_target": missing_in_target,
            "missing_in_source": missing_in_source,
            "discrepancies": discrepancies
        }