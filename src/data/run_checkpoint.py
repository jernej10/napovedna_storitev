import great_expectations as ge
from great_expectations.checkpoint.types.checkpoint_result import CheckpointResult
import pandas as pd


def main():
    context = ge.get_context()
    result: CheckpointResult = context.run_checkpoint(checkpoint_name="my_checkpoint")

    if not result["success"]:
        print("[Validate]: Checkpoint validation failed!")
    else:
        print("[Validate]: Checkpoint validation passed!")

    #dm = DataManager(data_path="data")
    #current = dm.get_dataframe("processed", "current_data")
    #dm.save("processed", "reference_data", current, override=True)

    #current_data = pd.read_csv("data/current_data.csv")
    #reference_data_path = "data/reference_data.csv"
    #current_data.to_csv(reference_data_path, index=False)

if __name__ == "__main__":
    main()