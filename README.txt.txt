#  Dashexperience: Football Performance Dashboard

Okiemute Blessing Albert-Ikolo

<a href="">OBAlbert-ikolo@uclan.ac.uk</a>

<!-- TABLE OF CONTENTS -->
<details>
  <summary><h2>Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#tools">Development tools</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

Dashexperience is a web-based football analytics dashboard built with Flask and Chart.js. It allows users to search, view, and compare real-time football player data using mainly but not subject to only the API-Football API service. The aim was to provide a modern, user-friendly interface for fans, analysts, or casual users to explore player stats, team info, league tables, and more — all in one place.
Users can search and view specific players ' profiles to see how they are doing during the current season, make up and compare two different players and their statistics, and get visual insights. They are also able to accress a live leaderboard of dirrent players ranked according to a mix of options from the user for statistics, leagues, and positions.
Everything maintains a dark theme for a nice, calm experience.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Development tools

- Python 3.11
- Flask
- Chart.js
- Bootstrap 5
- API-Football (via RapidAPI)
- HTML / CSS / JavaScript

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED --><!-- GETTING STARTED -->
## Getting Started

To run Dashexperience locally on your machine:

### Prerequisites

Make sure you have the following installed:

* Python 3.11
* pip (Python package manager)
* Git
* A code editor (e.g., VS Code)
* Internet connection for API calls

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/OBAlbert/dashexperience.git
   cd dashexperience

2. Create a virtual environment (optional but forteh best):
   ```sh
   python -m venv venv
    source venv/bin/activate
   ```
3. Install required packages
   ```sh
   pip install -r requirements.txt
   ```
4. Add your API-Football key:
   Open app.py and replace the X-RapidAPI-Key value with your key.
   Or create a .env file and store it securely.
   
5. Run the app
   ```sh
   flask run
   ```
6. Visit http://localhost:5000 in your browser

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->
## Usage

Once the app is running, you can use the following features:

- **Player Search**: Enter a name to find any player across top leagues. View detailed season stats and recent match history.
- **Player Comparison**: Select and compare two players side-by-side using visual charts and categorized stats.
- **Leaderboard**: View top-performing players filtered by league, stat type (e.g. goals, assists), and position.
- **League Table**: Select a league and view the current standings and squad details for each team.
- **Home Page**: Get an overview of the dashboard’s features and navigate easily between sections.

The dashboard uses a clean dark theme with green accents for a calm viewing experience and modern feel.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTACT -->
## Contact

Okiemute Blessing Albert-Ikolo  
OBAlbert-ikolo@uclan.ac.uk  
[GitHub Account](https://github.com/OBAlbert)

Project Link: [https://github.com/OBAlbert/dashexperience](https://github.com/OBAlbert/dashexperience)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

- [API-Football](https://www.api-football.com/) — for providing extensive and reliable football data.
- [Bootstrap 5](https://getbootstrap.com/) — for clean, responsive layouts and styling.
- [Chart.js](https://www.chartjs.org/) — for flexible and easy-to-use charts and visualizations.
- My peers and testers — for helping spot bugs and suggest improvements during tight deadlines!

<p align="right">(<a href="#readme-top">back to top</a>)</p>
