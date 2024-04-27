
# Revenue Estimation and Optimization for Presidents of EURL vs SASU

## Description

This project develops a Python API designed to compare key differences and relative advantages between two very common legal forms in France: SASU and EURL. The tool is designed to help entrepreneurs choose the most appropriate legal structure for their needs by providing a detailed comparative analysis based on various criteria such as taxation, liability, and management flexibility. The API allows querying and receiving structured data that can be integrated into business advisory applications or used individually for informed decision-making.

## Features

- Automated Comparison: The API offers an automated comparison feature between SASU and EURL, enabling users to obtain a comparative analysis based on predefined criteria such as taxation, shareholder liability, and administrative obligations.
- Tax Calculator: Incorporates a module capable of calculating the tax implications for each legal form, providing personalized estimates based on user inputs.
- Intuitive User Interface: Provides a simple interface for querying the API, suitable for users without advanced technical skills, facilitating access to critical information for decision-making.
- Detailed Reports: Generates detailed reports that can be downloaded or directly integrated into other applications, offering flexibility of use in various contexts, such as presentations or personalized consultations.
- Multilingual Support: Offers multilingual support to reach a broader audience, including but not limited to French and English.
- Integration of External Data: Ability to integrate external data to enrich analyses, such as economic data or business creation statistics, to provide a more comprehensive perspective.

## Technologies

- Python: Version 3.9
- Autres dépendances: listées dans `requirements.txt`

## Installation

To set up the necessary environment to run this project, follow the steps below:

1. Clone the repository to your local machine:
    ```bash
    git clone [GitHub repository URL]
    cd [directory name]
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Since this is a Streamlit application, ensure that Streamlit is installed. If not, install it using:
    ```bash
    pip install streamlit
    ```

4. [Add any additional instructions if necessary, such as configuration of environment variables or setting up a virtual environment.]

## Usage

To start the application, run the main script from the command line using Streamlit:

```bash
streamlit run app.py
```

[Si applicable, ajoutez ici des exemples d'utilisation ou des commandes spécifiques.]

## Projet Structure

- `app.py` : Point d'entrée principal de l'application.
- `modules/` : Contient des scripts Python supplémentaires ou des classes utilisées par l'application.
- `notebooks/` : Contient des Jupyter Notebooks pour des démonstrations ou des analyses supplémentaires.

## Contributing

To contribute to this project, please follow these steps:

1. Fork the project.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

## Licence

MIT License

Copyright (c) 2024 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Contact

Ludovic Gardy - ludovic.gardy@sotisanalytics.com