from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import date


load_dotenv()


# Load the API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")

# client = OpenAI()

client = OpenAI(api_key=api_key)


# Define the response model using Pydantic
class ProductDetails(BaseModel):
    name: str
    brand: str
    pack_size: str
    mfg_date: str
    exp_date: str
    mrp: str


def checkExpiryStatus(exp_date: str) -> str:
    """
    Check the expiry status of the product based on the expiry date.

    Args:
        exp_date (str): The expiry date of the product.

    Returns:
        str: The expiry status of the product.
    """
    # Convert the expiry date string to a date object
    try:
        exp_date = date.fromisoformat(exp_date)

        # Get the current date
        current_date = date.today()

        # Check if the product has expired
        if exp_date < current_date:
            return "expired"
        else:
            return "not expired"
    # for all errors
    except Exception as e:
        return "NA"


def get_product_details_from_text(text: str) -> dict:
    """
    Extracts product details from a given text using the GPT-4 model and returns them as a dictionary.

    Args:
        text (str): The input text containing product information.

    Returns:
        dict: A dictionary with product details.
    """
    # Set up the completion request to parse the response into the ProductDetails model
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Extract the product information. Give dates in the format dd/mm/yy. Make sure mfg date is before expiry date by analyzing the dates. Use real world knowledge to correct any errors like typos or incorrect dates. I want the product name, brand, pack size, manufacturing date, expiry date, and MRP.",
            },
            {"role": "user", "content": text},
        ],
        response_format=ProductDetails,
    )

    # Parse the response (returns a Pydantic model instance)
    parsed_response = completion.choices[0].message.parsed

    # Convert the Pydantic model instance to a dictionary using model_dump()
    product_details = parsed_response.model_dump()

    # add a new key-value pair to the dictionary
    product_details["status"] = checkExpiryStatus(product_details["exp_date"])

    return product_details


# # Example usage
# if __name__ == "__main__":
#     input_text = """Sunille chocolate, manufactured on 01/02/22, expires on 30/08/22, with a pack size of 80g. The price is Rs. 100."""
#     product_info = get_product_details_from_text(input_text)
#     print(product_info)


# # Define the response model using Pydantic
# class ProductDetails(BaseModel):
#     name: str
#     brand: str
#     pack_size: str
#     mfg_date: str
#     exp_date: str
#     mrp: str


# def get_product_details_from_text(text: str) -> dict:
#     """
#     Extracts product details from a given text using the GPT-4 model and returns them as a dictionary.

#     Args:
#         text (str): The input text containing product information.

#     Returns:
#         dict: A dictionary with product details.
#     """
#     # Set up the completion request to parse the response into the ProductDetails model
#     completion = client.beta.chat.completions.parse(
#         model="gpt-4o-2024-08-06",
#         messages=[
#             {"role": "system", "content": "Extract the product information."},
#             {"role": "user", "content": text},
#         ],
#         response_format=ProductDetails,
#     )

#     # Parse the response (returns a Pydantic model instance)
#     parsed_response = completion.choices[0].message.parsed

#     # Convert the Pydantic model instance to a dictionary
#     product_details = parsed_response.dict()

#     return product_details


# Example usage
if __name__ == "__main__":
    input_text = """['Sunille', 'Adk tntolsaly ricl cocoa"', 'v', '(roat (or Your sonses', '#Ax', '#66)', '4482uas PO LZADE Uas Lettll', 'K(ITiCcuo', 'I', 'JEZ', '~U', 'CG', 'OIC', 'JIE', 'ALZI', 'RMmkLLS ARD THRMNG', '8', '8', 'LOCAL Gornunitues', '9%', 'MIOCNiFLozg', '09 $', '2oan ZDroacok Z axeuement %br #erage adult per day', 'VAleaceeek', 'approx ? squares Of the chocolate', 'comVaadburybournville', 'Saoabn', 'SGE,;', 'Drled Swaetened Cranbarries Isg8', 'Lestoca ', 'AOZaaavour end NatunennedcerbetaeBy442 476}', 'Maradon EGOnWOlE and Nature Identes  Eavouring Substances)', 'Centalm Otno? Treo', 'Nut (Almond).', '"Relers (@ [Cocoa', 'DonoStoRon OORE NAESOOH HYGIENIG AND Dry PLACE', '0', '8enatrone novidite Khengature Tez56', '250', '0', 'Whutish tayer withour ', 'changes', 'cause produce to develop', 'Trademarks Op', 'Its fitness for Consumption', 'Mondalez Interational group Ueed undero', 'Doomuetouainn youane toc sansned nn to', 'Droduct gualty rerain the package', 'call', '1800 22 70807exalat sugge tionsoradizidiacc"', '#teto Mumbai address on pack', 'Nee WG:', '80 9', '{', 'Incla Foods Private Llrnited,', "a' Toive?", '3 0', 'Center', '4mm', ':ic. Hlo. 1001Q022002719', 'Inella Foode Privake Limited.', '73n8', '~4', '90012022001004', '622201"1384241', 'I2020B', '01/02/22', 'MRP Rs IOQ', '29/10/22', '(In"\'', '3', 't0s', '86644 ', 'Dietary', 'Solids;', 'Sugar)', 'Flvoua ', 'Flavour_', 'Ailcreoa ', 'Milka', 'Mov "', 'Nuts;', 'Soy:', 'Storage ', 'may', 'arfecting', 'license', 'Mondelez !', 'Pare .', 'Muty', '"delez ']"""
    product_info = get_product_details_from_text(input_text)
    print(product_info)
    print(type(product_info))
