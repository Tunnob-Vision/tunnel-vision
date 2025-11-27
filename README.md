# Tunnel Vision 🃏♠️

**AI-Powered Poker Decision Assistant with Computer Vision**

A comprehensive poker analysis tool that uses YOLOv8 for card detection and machine learning for strategic recommendations.

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Poker Terminology Guide](#-poker-terminology-guide)
- [Model Training](#-model-training)
- [Installation & Setup](#-installation--setup)
- [Running the Application](#-running-the-application)
- [User Guide](#-user-guide)
- [Testing](#-testing)
- [Technologies Used](#-technologies-used)
- [Experimental Features](#-experimental-features)
- [Deployment](#-deployment)

---

## 🎯 Project Overview

Tunnel Vision is a poker assistant application that combines computer vision and AI to help players make informed decisions. The system can:

1. Detect poker cards from photos using YOLOv8
2. Allow manual game state entry
3. Provide AI-powered action recommendations based on game context
4. Calculate hand equity and strength

---

## ✨ Features

### Computer Vision Module

- **Card Detection**: YOLOv8-based model trained on poker card dataset
- **Real-time Processing**: Upload or capture photos for instant card recognition
- **High Accuracy**: Detects suits and ranks with confidence scores

### Decision Engine

- **Strategic Analysis**: Evaluates game state considering pot odds, position, and opponents
- **Multiple Strategies**: Supports tight, balanced, and aggressive play styles
- **Hand Equity Calculation**: Computes winning probabilities
- **Contextual Recommendations**: Provides fold/call/raise suggestions with rationale

### User Interface

- **Dual Input Modes**: Photo upload or manual entry
- **Interactive Game State**: Track pot size, positions, betting rounds
- **Visual Feedback**: Clear card display and recommendation metrics
- **Responsive Design**: Built with Streamlit for smooth interaction

---

## 🏗️ Architecture

```
tunnel-vision/
├── cv/src/              # Computer Vision module
│   ├── card_detector.py # YOLOv8 inference
│   ├── card_parser.py   # Detection to Card conversion
│   └── train_poker.py   # Model training script
├── ml/src/              # Machine Learning module
│   ├── decision_engine.py # AI recommendation engine
│   └── equity.py        # Hand equity calculations
├── views/               # Frontend pages
│   ├── upload_page.py   # Photo upload interface
│   └── confirmation_page.py # Game state & recommendations
├── utils/               # Data models
│   └── models.py        # Card, Hand, Community, GameState
├── models/              # Trained models
│   └── best.pt          # YOLOv8 trained weights
├── tests/               # Test suite
└── app.py               # Main Streamlit application
```

---

## 🎴 Poker Terminology Guide

For users unfamiliar with poker terms, here's a quick reference:

### Game Elements

| Term                | Definition                                           |
| ------------------- | ---------------------------------------------------- |
| **Hole Cards**      | The 2 private cards dealt to each player (your hand) |
| **Community Cards** | Shared cards visible to all players (the board)      |
| **Pot**             | Total amount of chips bet in the current hand        |
| **Stack**           | Total chips a player has available                   |

### Betting Rounds (Streets)

| Street       | Description                            | Community Cards |
| ------------ | -------------------------------------- | --------------- |
| **Pre-Flop** | Before any community cards             | 0 cards         |
| **Flop**     | First betting round after initial deal | 3 cards         |
| **Turn**     | Fourth community card                  | 4 cards         |
| **River**    | Fifth and final community card         | 5 cards         |

### Actions

| Action    | Description                                           |
| --------- | ----------------------------------------------------- |
| **Fold**  | Discard your hand and forfeit the pot                 |
| **Call**  | Match the current bet to stay in the hand             |
| **Raise** | Increase the current bet amount                       |
| **Check** | Pass action without betting (when no bet is required) |

### Table Position

| Position   | Description                    | Strategic Advantage    |
| ---------- | ------------------------------ | ---------------------- |
| **Early**  | First to act after blinds      | Least information      |
| **Middle** | Mid-position seats             | Moderate information   |
| **Late**   | Last to act (button area)      | Most information       |
| **Blinds** | Forced bets before cards dealt | Disadvantaged position |

### Key Metrics

- **Pot Odds**: Ratio of pot size to call amount (helps determine if calling is profitable)
- **Equity**: Your probability of winning the hand (expressed as percentage)
- **Amount to Call**: Chips required to stay in the hand
- **Minimum Raise**: Smallest legal raise size

---

## 🤖 Model Training

### Dataset

- **Source**: [Roboflow poker card detection dataset](https://universe.roboflow.com/poker001/poker-j2pzb/dataset/4)
- **Classes**: 52 classes (13 ranks × 4 suits)
- **Split**: Train/Valid/Test sets with augmentation

### Training the YOLOv8 Model

#### Simplest way (Google Colab)

1. Open [this Colab notebook](https://colab.research.google.com/drive/1WXYdeStb2bVMaYbkCq62xmp05f11uU8N?usp=sharing)

2. Import the zip dataset from Roboflow

3. Select GPU runtime

4. Run all cells to train the model

#### Else do it on your own computer: Prerequisites

```bash
pip install -r requirements.txt
```

#### Training Script

```bash
python cv/src/train_poker.py
```

#### Training Configuration

- **Model**: YOLOv8 Nano
- **Epochs**: 10
- **Image Size**: 640×640
- **Optimizer**: AdamW
- **Data Augmentation**: Rotation, scaling, brightness adjustments

#### Training Output

- Model weights saved to: `runs/detect/YOLO-Nano_10-epochs_Size-640/weights/best.pt`
- Training metrics: `results.csv`
- Configuration: `args.yaml`

### Using Pre-trained Model

The repository includes a pre-trained model at `models/best.pt` ready for inference.

---

## 🚀 Installation & Setup

### Option 1: Manual Setup

## 1) Create a virtual environment

- Windows (PowerShell):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

- Windows (Command Prompt):

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

- Windows (Git Bash):

```bash
python -m venv venv
source venv/Scripts/activate
```

- macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

To deactivate later:

```bash
deactivate
```

## 2) Install dependencies

```bash
pip install -r requirements.txt
```

### Dependencies Include:

- **streamlit**: Web application framework
- **ultralytics**: YOLOv8 for object detection
- **opencv-python**: Image processing
- **torch**: Deep learning framework
- **pytest**: Testing framework

---

## 🎮 Running the Application

### Start the Streamlit App

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Usage Workflow

#### Photo Upload Mode:

1. Click **"Start Photo Upload"**
2. Upload or capture a photo of your poker hand
3. Review detected cards
4. Enter game context (pot size, position, opponents)
5. Get AI recommendation

#### Manual Entry Mode:

1. Click **"Enter Game State"**
2. Select your 2 hole cards
3. Choose current street (Pre-Flop/Flop/Turn/River)
4. Select community cards
5. Enter betting information
6. Configure table information
7. Get AI recommendation

---

## 📖 User Guide

### Confirmation Page Features

The confirmation page is the heart of the application where you input game state and receive AI recommendations. Here's what you can do:

#### 1️⃣ Hand Selection

- **Select your 2 hole cards** from the dropdown
- Cards are displayed in standard poker notation (e.g., "A♠" = Ace of Spades)
- System validates that exactly 2 cards are selected
- Real-time feedback: ✓ shows when selection is valid

#### 2️⃣ Game Street Selector (Manual Entry Only)

- Choose the current betting round: **Pre-Flop**, **Flop**, **Turn**, or **River**
- Automatically limits community card selection based on street
- Pre-Flop = 0 cards, Flop = 3 cards, Turn = 4 cards, River = 5 cards

#### 3️⃣ Community Cards (Board)

- Select board cards visible to all players
- Cards are displayed visually with labels (Flop, Flop, Flop, Turn, River)
- System prevents duplicate selection between your hand and board
- Validation ensures correct number of cards for selected street

#### 4️⃣ Betting Information

Configure the current betting situation:

- **Pot Size**: Total chips in the pot (default: 50)
- **Amount to Call**: Chips needed to stay in hand (default: 10)
- **Your Stack**: Total chips you have available (default: 1000)
- **Minimum Raise**: Smallest legal raise size (auto-calculated: 2× call amount)

#### 5️⃣ Table Information

Provide context about the table:

- **Your Position**: Select Early/Middle/Late/Blinds (affects strategy)
- **Number of Opponents**: How many active players (1-9, default: 2)

#### 6️⃣ Strategy & Notes

Customize AI behavior:

- **Strategy Profile**:
  - **Tight**: Conservative, risk-averse play
  - **Balanced**: Mixed approach (default)
  - **Aggressive**: Bold, high-pressure play
- **Opponent Notes**: Optional text field for observations (e.g., "Player 3 bluffs often")

#### 7️⃣ Summary Dashboard (Manual Entry Only)

Real-time overview of your game state:

- Current street and position
- Pot size and amount to call
- Your stack and opponent count
- Updated automatically as you change inputs

### Action Buttons

#### Manual Entry Mode:

- **🔄 Reset Form**: Clear all inputs and start fresh
- **💾 Save Game State**: Store current configuration in session
- **💡 Get AI Recommendation**: Analyze game state and receive action advice

#### Photo Upload Mode:

- **✅ Confirm Hand**: Accept detected cards
- **🔄 Retry Analysis**: Return to upload page and try again
- **💡 Get AI Recommendation**: Get action advice with confirmed cards

### AI Recommendation Output

When you click "Get AI Recommendation", the system displays:

#### 📊 Metrics Dashboard

- **Recommended Action**: Fold 🚫 / Call ✅ / Raise 📈
- **Confidence**: AI's certainty in the recommendation (0-100%)
- **Bet Size**: Suggested raise amount (if applicable)
- **Equity**: Your winning probability against opponents

#### 📝 Detailed Rationale

Expandable section explaining:

- Why this action is recommended
- Pot odds analysis
- Hand strength evaluation
- Position and opponent considerations
- Risk/reward assessment

### Validation & Error Handling

The system provides real-time feedback:

- ✅ Success messages when inputs are valid
- ⚠️ Warnings for incomplete selections
- ❌ Error messages for invalid states:
  - Duplicate cards detected
  - Wrong number of community cards for street
  - Missing hole card selection

### Hand Strength Display

When you have hole cards + at least 3 community cards:

- Shows your current made hand (e.g., "Pair of Aces", "Flush", "Straight")
- Displays percentile ranking: "Beats roughly 85% of other hands on this board"
- Updates automatically as you add/remove community cards

---

## 🧪 Testing

**Without coverage:**

```bash
pytest tests/
```

**With coverage report:**

```bash
pytest tests/ --cov=. --cov-report=term-missing
```

**Generate HTML coverage report:**

```bash
pytest tests/ --cov=. --cov-report=html
```

Then open `htmlcov/index.html` in your browser.

## 🛠️ Technologies Used

### Computer Vision

- **YOLOv8** (Ultralytics): Real-time object detection
- **OpenCV**: Image processing and manipulation
- **PyTorch**: Deep learning backend

### Machine Learning

- **Custom Decision Engine**: Rule-based + statistical analysis
- **Equity Calculator**: Monte Carlo simulation

### Frontend

- **Streamlit**: Interactive web application framework
- **Python**: Core language

### Testing & Quality

- **pytest**: Unit and integration testing
- **pytest-cov**: Code coverage analysis

---

## 🔬 Experimental Features

### Hand Gesture Recognition (Not Merged)

We explored implementing hand gesture recognition to detect player actions (check, fold, raise) through video input. This feature was developed in a separate branch but encountered challenges.

While this feature is not in the main branch for submission, the experimental work demonstrates our exploration of advanced computer vision techniques. We'll be happy to discuss this development during the oral presentation.

---

## 🌐 Deployment

### Live Application

The app is deployed and running at: **https://tunnel-vision.streamlit.app**

### Deployment Platform

- **Streamlit Cloud**: Free hosting for Streamlit apps
- **Auto-deployment**: Connected to GitHub repository
- **Environment**: Python with all dependencies from requirements.txt

---

## 📝 Key Files

| File                       | Description                        |
| -------------------------- | ---------------------------------- |
| `app.py`                   | Main application entry point       |
| `requirements.txt`         | Python dependencies                |
| `models/best.pt`           | Trained YOLOv8 model (52 classes)  |
| `cv/src/dataset/data.yaml` | Dataset configuration for training |

## 🔗 Repository

**GitHub**: [Tunnob-Vision/tunnel-vision](https://github.com/Tunnob-Vision/tunnel-vision)
