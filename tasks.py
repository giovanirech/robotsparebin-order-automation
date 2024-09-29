from robocorp.tasks import task, get_output_dir
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.PDF import PDF
from pathlib import Path
import pandas as pd
import logging
import shutil

logger = logging.getLogger(__name__)

MAX_SUBMISSION_ATTEMPTS = 5

RECEIPTS_PATH = Path(get_output_dir()) / "receipts"
IMAGES_PATH = Path(get_output_dir()) / "images"
PDFS_PATH = Path(get_output_dir()) / "pdfs"

if not RECEIPTS_PATH.exists():
    RECEIPTS_PATH.mkdir()

if not IMAGES_PATH.exists():
    IMAGES_PATH.mkdir()

if not PDFS_PATH.exists():
    PDFS_PATH.mkdir()


@task
def order_robots_from_RobotSpareBin():
    """
    Automates the process of ordering robots from RobotSpareBin Industries Inc.

    This function performs the following steps:

    - Downloads the orders CSV file and loads it into a DataFrame.
    - Opens the RobotSpareBin website and navigates to the order page.
    - Closes any modal dialogs that appear.
    - Retrieves model parts information and maps part numbers to model names.
    - For each order in the orders DataFrame:
        - Fills out the order form.
        - Previews the order.
        - Submits the order, retrying if necessary.
        - Saves the order receipt as a PDF file.
        - Takes a screenshot of the ordered robot.
        - Embeds the screenshot into the PDF receipt.
    - Creates a ZIP archive of the receipts and images.

    Notes
    -----
    The function relies on several helper functions to perform specific tasks.

    Examples
    --------
    >>> order_robots_from_RobotSpareBin()
    """
    # Download the orders CSV file and load it
    orders_df = get_orders()

    # Open the browser and access the RobotSpareBin website, go to place order page
    open_robot_order_website()
    go_to_place_order_page()
    close_annoying_modal()

    model_parts_dict = get_model_parts()
    # Map the part numbers to the model names
    orders_df["Head"] = orders_df["Head"].map(model_parts_dict)

    # Loop through the orders:
    for i, row in orders_df.iterrows():
        close_annoying_modal()
        fill_the_form(row)
        preview_order()
        submit_until_success()
        receipt_path = store_receipt_as_pdf(row["Order number"])
        screenshot_path = screenshot_robot(row["Order number"])
        embed_screenshot_to_receipt(row["Order number"], screenshot_path, receipt_path)
        click_order_another()

    # Create ZIP archive of the receipts and the images
    archive_receipts()


def open_robot_order_website():
    """
    Opens the RobotSpareBin Industries website in the browser.

    This function navigates to the main page of the RobotSpareBin Industries website.

    See Also
    --------
    go_to_place_order_page : Navigates to the place order page.
    """
    browser.goto("https://robotsparebinindustries.com")


def get_orders() -> pd.DataFrame:
    """
    Downloads the orders CSV file and loads it into a DataFrame.

    Returns
    -------
    orders_df : pandas.DataFrame
        DataFrame containing the orders data.

    Notes
    -----
    The orders CSV file is downloaded from a predefined URL and saved to the output directory.
    """
    output_path = get_output_dir() / "orders.csv"
    HTTP().download(
        "https://robotsparebinindustries.com/orders.csv", output_path, overwrite=True
    )
    orders_df = pd.read_csv(output_path)
    return orders_df


def go_to_place_order_page():
    """
    Navigates to the 'Order' page on the RobotSpareBin Industries website.

    This function clicks on the link that directs the user to the order placement page.

    See Also
    --------
    open_robot_order_website : Opens the main website.
    """
    page = browser.page()
    page.click("//a[contains(text(),'Order')]")


def close_annoying_modal():
    """
    Closes any modal dialogs that appear on the page.

    This function waits for a modal dialog to appear and closes it by clicking the 'OK' button.

    Notes
    -----
    If the modal does not appear within the specified timeout, a warning is logged.
    """
    page = browser.page()
    try:
        page.wait_for_selector("//div[@class='modal']", timeout=2000)
        page.click("//button[contains(text(), 'OK')]")
    except Exception as e:
        logger.warning(f"Modal did not appear: {e}")


def get_model_parts():
    """
    Retrieves the model parts information from the website.

    This function clicks a button to display the model information table,
    extracts the table, and converts it into a dictionary mapping part numbers to model names.

    Returns
    -------
    parts_dict : dict
        Dictionary mapping part numbers (str) to model names (str).

    Notes
    -----
    The function uses pandas to parse the HTML table into a DataFrame for easier manipulation.
    """
    page = browser.page()

    # Click button to show table
    page.click("//button[contains(text(), 'Show model info')]")

    # Get the HTML table
    html_table = page.locator("//table[@id='model-info']").inner_html()
    html_table = "<table>" + html_table + "</table>"

    # Convert the table into a DataFrame for easier manipulation
    df = pd.read_html(str(html_table))[0]

    # Convert the DataFrame into a dictionary
    table_dict = df.to_dict(orient="records")

    parts_dict = {
        item["Part number"]: item["Model name"]
        for item in table_dict
    }

    return parts_dict


def fill_the_form(row: pd.Series):
    """
    Fills out the robot order form with the given order data.

    Parameters
    ----------
    row : pandas.Series
        A Series containing the order data. Expected to have the following fields:
        - 'Order number' : str
        - 'Head' : str
        - 'Body' : str or int
        - 'Legs' : str or int
        - 'Address' : str

    Notes
    -----
    The function interacts with various form elements on the page to fill in the order details.
    """
    _, head, body, legs, address = row

    page = browser.page()
    # Fill Head (dropdown)
    print(head)
    page.select_option("//select[@id='head']", head + ' head', timeout=3000)
    # Fill Body (radio button)
    page.check(f"//input[@type='radio'][@name='body'][@id='id-body-{body}']")
    # Fill Legs (number)
    page.fill("//input[@placeholder='Enter the part number for the legs']", str(legs))
    # Fill Address (textarea)
    page.fill("//input[@id='address']", address)


def preview_order():
    """
    Clicks the 'Preview' button to preview the robot order.

    Notes
    -----
    This function triggers the robot preview, allowing for a screenshot to be taken later.
    """
    page = browser.page()
    # Preview robot
    page.click("//button[@id='preview']")


def submit_until_success():
    """
    Submits the order form, retrying until successful or until the maximum number of attempts is reached.

    Notes
    -----
    The function will attempt to submit the order up to `MAX_SUBMISSION_ATTEMPTS` times,
    checking for success after each attempt. If the submission fails, it will retry.
    """
    page = browser.page()
    success = False
    count = 0
    while (not success) and count <= MAX_SUBMISSION_ATTEMPTS:
        count += 1
        # Submit order
        page.click("//button[@id='order']")
        success = check_order_success()
        if not success:
            print("Failed to submit order, retrying...")
            logger.warning("Failed to submit order, retrying...")


def check_order_success():
    """
    Checks whether the order was submitted successfully.

    Returns
    -------
    success : bool
        True if the order was submitted successfully, False otherwise.

    Notes
    -----
    The function checks for the presence of an error message on the page.
    If an error message is visible, it assumes the submission failed.
    """
    page = browser.page()
    # Check if warning message is present
    webelement = page.locator("//div[@class='alert alert-danger'][@role='alert']")
    has_error_message = webelement.is_visible()
    if has_error_message:
        return False
    else:
        return True


def click_order_another():
    """
    Clicks the 'Order Another' button to reset the form for the next order.

    Notes
    -----
    This function prepares the form for the next order by clicking the appropriate button.
    """
    page = browser.page()
    page.click("//button[@id='order-another']")


def store_receipt_as_pdf(order_number: str) -> Path:
    """
    Saves the order receipt as a PDF file.

    Parameters
    ----------
    order_number : str
        The order number used to name the PDF file.

    Returns
    -------
    receipt_path : pathlib.Path
        The path to the saved PDF receipt.

    Notes
    -----
    The function extracts the receipt HTML from the page and converts it to a PDF file.
    """
    page = browser.page()
    receipt_html = page.locator("//div[@id='receipt']").inner_html()
    receipt_path = RECEIPTS_PATH / f"receipt_{order_number}.pdf"
    pdf_constructor = PDF()
    pdf_constructor.html_to_pdf(receipt_html, receipt_path)
    return receipt_path


def screenshot_robot(order_number: str) -> Path:
    """
    Takes a screenshot of the robot preview.

    Parameters
    ----------
    order_number : str
        The order number used to name the screenshot file.

    Returns
    -------
    screenshot_path : pathlib.Path
        The path to the saved screenshot image.

    Notes
    -----
    The function captures the robot preview image and saves it as a PNG file.
    """
    page = browser.page()
    robot_locator = page.locator("//div[@id='robot-preview-image']")
    screenshot_path = IMAGES_PATH / f"screenshot_{order_number}.png"
    robot_locator.screenshot(path=screenshot_path)
    return screenshot_path


def embed_screenshot_to_receipt(order_number: str, screenshot: Path, pdf_file: Path):
    """
    Embeds the robot screenshot into the PDF receipt.

    Parameters
    ----------
    order_number : str
        The order number used to name the output PDF file.
    screenshot : pathlib.Path
        The path to the screenshot image file.
    pdf_file : pathlib.Path
        The path to the original PDF receipt file.

    Notes
    -----
    The function combines the PDF receipt and the screenshot image into a single PDF file.
    The output file is saved in the PDFs directory.
    """
    pdf_constructor = PDF()
    output_path = PDFS_PATH / f"receipt_with_screenshot_{order_number}.pdf"
    pdf_constructor.add_files_to_pdf(
        [pdf_file, screenshot], target_document=output_path, append=False
    )


def archive_receipts():
    """
    Creates a ZIP archive of the receipts and images.

    Notes
    -----
    The function compresses the PDFs directory into a ZIP file named 'robot_orders_receipts.zip'.
    """
    zip_path = shutil.make_archive(
        get_output_dir() / "robot_orders_receipts", "zip", root_dir=PDFS_PATH
    )
    print(f"ZIP archive created: {zip_path}")
