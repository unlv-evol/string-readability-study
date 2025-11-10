# String Interpolation Experiment - Replication Packet
## Overview
Literal string interpolation is a widely-used programming language construct that enables developers to embed variables, expressions, and/or functions within a string. It is consider to be more concise compared to traditional concatenation approach. The syntax of string interpolation can vary significantly between different programming languages. However, its impact on program readability and comprehension remains unexplored. Therefore, the objective of this study is to investigate the effect of literal string interpolation on program readability and comprehension.
## Directory Structure
The replication packet consist of the experiment software, data analysis scripts and figures.
- [`analysis`](analysis): contains helper files used in the main files. There are 9 helper files.
  - [figures](figures): all figures generated from data analysis using quorum
  - [quorum_scripts](quorum_scripts): quorum project contain all the script and data for reproducing the statistically analysis and figures.
- [data](data): data for all the phases of the experiment. The latest is `responses_phase_3.csv` and it is what we used in the paper.

The rest of the folders and files are associated with the experiment software. 
## Tool Setup
To replicate the experiment, you can simply follow the steps below to setup the data gathering tool.
### Installation and Usage
1. **Running locally**
   - Setup the  by cloning the repository using `git clone` or download the repository.
   - It is a good practice to configure python virtual environment. Use the commands below to setup python virtual environment on `Linux/MacOS` or `Windows OS`. NB: The tool is designed using `Python 3.10` and tested on `Python 3.8` and `Python 3.9`.
   ```
   # For Linux/MacOS

   python3 -m venv venv
   source venv/bin/activate
   ```
   - For `Window OS` user, the easiest approach is to install `virtualenv` by running `pip install virtualenv`. The next step is pretty much similar to above;
   ```
   # For Window OS

   python3 -m virtualenv venv
   venv\Scripts\activate
   ```
   - Install required dependencies using `pip3 install -r requirements.txt`
   - Start the `experiment` by running `python3 app.py`. Ensure that port `5000` is open on your firewell. To interact with the experiment, go to your browser and type `localhost:5000` or `127.0.0.1:5000`.

2. **Running locally with "Docker for Desktop" - Not Yet Fully Tested!!**
   - Download and install `Docker fo Desktop` using the [link](https://www.docker.com/products/docker-desktop/). Once you are all set, run the commands below;
   ```
   git clone <project>
   cd /<project>
   docker compose up -d
   ```
  - That's all 😎!! the tool will be running on port `5000`. To interact with the experiment, go to your browser and type `localhost:5000`. You should be able to see the consent page of the experiment.
  
**NB: The ouput of the experiment will be stored in the [data](data) folder with the file name `responses.csv`**

## Issues 
Incase you encounter any challenge trying to reproduce this experiment, please feel free to report to the corresponding author of the paper.