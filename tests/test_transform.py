import pandas as pd

from src.transform import clean_sales_data


def test_clean_sales_data_standardizes_columns_and_features() -> None:
    raw_df = pd.DataFrame(
        {
            "Row ID": [1, 2],
            "Order ID": [100, 101],
            "Order Date": ["2012-01-01", "2012-01-02"],
            "Order Priority": ["High", "Low"],
            "Order Quantity": [2, 1],
            "Sales": [100.0, 50.0],
            "Discount": [0.1, 0.0],
            "Ship Mode": ["Regular Air", "Delivery Truck"],
            "Profit": [15.0, -5.0],
            "Unit Price": [50.0, 50.0],
            "Shipping Cost": [5.0, 8.0],
            "Customer Name": ["Alice", "Alice"],
            "Province": ["Ontario", "Ontario"],
            "Region": ["Ontario", "Ontario"],
            "Customer Segment": ["Consumer", "Consumer"],
            "Product Category": ["Technology", "Furniture"],
            "Product Sub-Category": ["Phones", "Chairs"],
            "Product Name": ["Desk Phone", "Desk Chair"],
            "Product Container": ["Small Box", "Large Box"],
            "Product Base Margin": [0.4, None],
            "Ship Date": ["2012-01-03", "2012-01-04"],
        }
    )

    clean_df = clean_sales_data(raw_df)

    assert "sales_amount" in clean_df.columns
    assert "customer_id" in clean_df.columns
    assert "product_id" in clean_df.columns
    assert "customer_type" in clean_df.columns
    assert clean_df["ship_delay_days"].tolist() == [2, 2]
    assert clean_df["customer_order_number"].tolist() == [1, 2]
