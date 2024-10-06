# Edify
Edify is an innovative edtech platform designed for college and high school students to enhance their academic performance. By leveraging AI technology, Edify helps students identify their strengths and weaknesses in their current knowledge state, providing personalized learning experiences.

## Table of Contents
- [Project Overview](#project-overview)
- [Target Audience](#target-audience)
- [Core Features](#core-features)
- [Technologies Used](#technologies-used)
- [Deployment](#deployment)
- [External Services](#external-services)
- [Installation Instructions](#installation-instructions)
- [Usage](#usage)
- [Contribution Guidelines](#contribution-guidelines)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Project Overview
Edify assists students in evaluating their current knowledge state against their academic goals. It analyzes individual strengths and weaknesses, then provides tailored opportunities for improvement through personalized notes and practical references. Additionally, it recommends the best platforms and sources for further study, promoting genuine learning rather than rote memorization.

## Target Audience
- College students
- High school students

## Core Features
- AI-driven analysis of students' strengths and weaknesses
- Personalized notes for weak topics with practical references
- Recommendations for additional resources to deepen knowledge

## Technologies Used
- **Backend:** Python (Flask for web services)
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite (for local database)
- **AI Services:** OpenAI GPT-4 (requires API key)

## Deployment
Currently, Edify must be deployed locally on your machine.
For this event, you can also access our model at: http://65.1.209.122/

## External Services
Edify utilizes OpenAI's GPT-4 for its AI services. To use this functionality, you must add your `OPENAI_API_KEY` to the `.env` file.

## Installation Instructions
To install and run Edify, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/pratyakshkwatra/edify
   ```
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```
3. Activate the virtual environment:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
4. Install the required packages:
   ```bash
   pip3 install -r requirements.txt
   ```
5. Ensure that the `.env` file is present and contains your `OPENAI_API_KEY`.
6. Run the Flask server:
   ```bash
   python3 server.py
   ```
7. Access the platform in your browser at `http://localhost:80`. If the port is not working, you can change the port in `server.py` and restart the Flask server.

## Usage
Once the server is running, navigate to the appropriate URL in your web browser to access the Edify platform and begin your learning journey!

## Contribution Guidelines
Contributions to Edify are welcome! If you have suggestions or improvements, feel free to submit an issue or a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
We would like to thank all the contributors and mentors who have supported the development of Edify. Special thanks to the OpenAI team for providing the GPT-4 API.# edify
# edify
