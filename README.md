<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->

<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<div align="center">
  <a href="https://github.com/larry-lime/airline-ticket-system">
    <img src="images/logo-color.png" alt="Logo" width="150" style="border-radius: 50%;">
  </a>

  <p align="center">
This project is a simple airline ticket system that allows customers, booking agents, and airline staff to book tickets, search for flights, and view flight statistics.
    <br />
    <a href="https://github.com/larry-lime/airline-ticket-system"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/larry-lime/airline-ticket-system">View Demo</a>
    ·
    <a href="https://github.com/larry-lime/airline-ticket-system/issues">Report Bug</a>
    ·
    <a href="https://github.com/larry-lime/airline-ticket-system/issues">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#deploy-with-docker">Deploy with Docker</a></li>
        <li><a href="#deploy-locally">Deploy Locally</a></li>
      </ul>
    </li>
    <!-- <li><a href="#usage">Usage</a></li> -->
    <li><a href="#roadmap">Roadmap</a></li>
    <!-- <li><a href="#contributing">Contributing</a></li> -->
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <!-- <li><a href="#acknowledgments">Acknowledgments</a></li> -->
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

- [![Flask][Flask.palletsprojects.com]][Flask-url]
- [![Docker][Docker.com]][Docker-url]
- [![Bootstrap][Bootstrap.com]][Bootstrap-url]
- [![MySQL][MySQL.com]][MySQL-url]

<!-- GETTING STARTED -->

## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Deploy with Docker

1. Ensure you have [Docker](https://www.docker.com/) installed.
   ```sh
   docker --version
   ```
2. Clone the repo
   ```sh
   git clone https://github.com/larry-lime/airline-ticket-system
   cd airline-ticket-system
   ```
3. Run docker compose
   ```sh
   docker compose up -d --build
   ```
4. Open [http://localhost:8000](http://localhost:8000) in your browser

### Deploy Locally

1. Add a `.env` file to the root directory. The file should contain the following environment variables:
   ```sh
   MYSQLHOST=your_mysql_host
   MYSQLUSER=root
   MYSQLPASSWORD=your_mysql_root_password
   MYSQLDATABASE=airline
   ```
2. Create Python virtual environment
   ```sh
   python3 -m venv .venv
   ```
3. Start virtual environment

   ```sh
   . .venv/bin/activate
   ```

4. Install requirements

   ```sh
   pip3 install -r requirements.txt
   ```

5. Initialize database

   ```sh
   flask --app airline init-db
   ```

6. Start development server

   ```sh
   flask --app airline run --debug
   ```

7. Open [http://localhost:5000](http://localhost:5000) in your browser

<!-- USAGE EXAMPLES -->

<!-- ## Usage -->
<!---->
<!-- Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources. -->
<!---->
<!-- _For more examples, please refer to the [Documentation](https://example.com)_ -->

<!-- ROADMAP -->

## Roadmap

- [ ] Add icons to the frontend
- [ ] Have a form send you an email when a new user signs up
- [ ] Add foreign currency support
- [ ] Ask use to use their current location
- [ ] Generate articles based on airport locations
- [ ] Add foreign language support. Auto translate everything?
- [ ] Add ability to login with third party services (Google, Facebook, etc.)
- [ ] Add a reccomentation system for articles
  - [ ] Reccomend them based on their flight purchases (and search history if you want to store that)
  - [ ] Does not need to use machine learning. It can simply use keywords
  - [ ] Alternatively, you can use some NLP library

<!-- LICENSE -->

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<!-- CONTACT -->

## Contact

Lawrence Lim - [@lawrence_lim\_\_](https://twitter.com/lawrence_lim__) - ll4715@nyu.edu.com

Project Link: [https://github.com/larry-lime/airline-ticket-system](https://github.com/larry-lime/airline-ticket-system)

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/github/contributors/larry-lime/airline-ticket-system.svg?style=for-the-badge
[contributors-url]: https://github.com/larry-lime/airline-ticket-system/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/larry-lime/airline-ticket-system.svg?style=for-the-badge
[forks-url]: https://github.com/larry-lime/airline-ticket-system/network/members
[stars-shield]: https://img.shields.io/github/stars/larry-lime/airline-ticket-system.svg?style=for-the-badge
[stars-url]: https://github.com/larry-lime/airline-ticket-system/stargazers
[issues-shield]: https://img.shields.io/github/issues/larry-lime/airline-ticket-system.svg?style=for-the-badge
[issues-url]: https://github.com/larry-lime/airline-ticket-system/issues
[license-shield]: https://img.shields.io/github/license/larry-lime/airline-ticket-system.svg?style=for-the-badge
[license-url]: https://github.com/larry-lime/airline-ticket-system/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/lawrence-rx-lim
[product-screenshot]: images/product-screenshot.jpg
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[Flask.palletsprojects.com]: https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white
[Flask-url]: https://flask.palletsprojects.com/en/2.3.x/
[Docker.com]: https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/
[MySQL.com]: https://img.shields.io/badge/mysql-%2300000f.svg?style=for-the-badge&logo=mysql&logoColor=white
[MySQL-url]: https://www.mysql.com/
