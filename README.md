# 🤖 RobotSpareBin Industries Order Automation

Welcome to the **RobotSpareBin Industries Order Automation** project! This automation script is designed to streamline the process of ordering robots from RobotSpareBin Industries Inc. 🛍️✨

This project was developed as part of the Automation Certification Level II of Robocorp and serves as a demonstration of advanced robotic process automation (RPA) techniques using Python and Robocorp's tools.

## 📚 Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Introduction

This automation project performs the following tasks:

- Downloads orders from a CSV file.
- Navigates to the RobotSpareBin Industries website.
- Fills out and submits order forms automatically.
- Saves order receipts as PDF files.
- Takes screenshots of the ordered robots.
- Embeds robot images into the PDF receipts.
- Archives all receipts and images into a ZIP file.

## Features

- **Web Automation**: Automates web interactions using `robocorp-browser`.
- **Data Processing**: Reads and processes order data from a CSV file using `pandas`.
- **PDF Manipulation**: Generates and modifies PDF files using `RPA.PDF`.
- **Error Handling**: Includes robust error handling and retries for form submissions.
- **Cross-Platform**: Configured to run on Windows, Linux, and macOS.

## Prerequisites

- **Python 3.10.12**
- **Robocorp Lab** or **VS Code** with [Robocorp extensions](https://sema4.ai/docs/automation/visual-studio-code)
- [Robocorp CLI (`rcc`)](https://sema4.ai/docs/automation/rcc/overview)
- **Git**

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/giovanirech/robotsparebin-order-automation.git
   cd robotsparebin-order-automation
   ```

**NOTE:** If you open this project on VS Code with the Robocorp extensions, the environment will be automatically set up for you, in which case you may skip steps 2 and 3.

2. **Set Up the Environment**

   Make sure you have `rcc` installed. Then create the conda environment:

   ```bash
   rcc environment create --path .
   ```

   This command will read the `conda.yaml` file and set up the environment accordingly.

3. **Verify the Environment**

   Confirm that the environment is set up correctly:

   ```bash
   rcc environment verify
   ```

## Usage

To run the automation script, execute the following command:

```bash
rcc run
```

Alternatively, you can run the task directly using Python:

```bash
python -m robocorp.tasks run tasks.py
```

The output (receipts, images, and the ZIP archive) will be saved in the `output/` directory.

## Project Structure

```
├── tasks.py               # Main automation script
├── conda.yaml             # Conda environment configuration
├── robot.yaml             # Robot configuration for Robocorp
├── output/                # Directory for output files
│   ├── receipts/          # PDF receipts
│   ├── images/            # Robot screenshots
│   └── pdfs/              # PDFs with embedded screenshots
└── README.md              # Project README file
```

## How It Works

1. **Download Orders 📥**

   The bot downloads the orders CSV file from the RobotSpareBin Industries website using the `RPA.HTTP` library.

2. **Open Website and Navigate 🌐**

   It opens the RobotSpareBin Industries website and navigates to the order placement page using `robocorp-browser`.

3. **Retrieve Model Information 🔍**

   The bot extracts the model part numbers and names from the website's table to map them correctly. It uses `pandas` to parse the HTML table.

4. **Process Orders 📝**

   For each order in the CSV file:

   - **Fill the Form**: Automatically fills out the order form fields.
   - **Preview Order**: Previews the robot to generate an image.
   - **Submit Order**: Submits the form, retrying if necessary.
   - **Save Receipt**: Saves the order receipt as a PDF file.
   - **Take Screenshot**: Captures a screenshot of the robot preview.
   - **Embed Image**: Embeds the robot screenshot into the PDF receipt.

5. **Archive Receipts 🗄️**

   After processing all orders, the bot creates a ZIP archive of all receipts and images for easy sharing or storage.


## License

This project is licensed under the Apache License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- **Robocorp**: For providing the tools and documentation to make RPA accessible.
- **RobotSpareBin Industries Inc.**: For the sample website used in this automation.
- **Emojis**: Emojis provided by [Emojipedia](https://emojipedia.org/).

---

Feel free to reach out if you have any questions or suggestions! 🚀