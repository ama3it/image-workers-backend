# Project Setup Guide

Follow these steps to set up and run the project locally.

## Prerequisites

- [Git](https://git-scm.com/)
- [Anaconda/Miniconda](https://docs.conda.io/en/latest/miniconda.html)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ama3it/image-workers-backend.git
   cd your-repo

2. **Create a .env file:**

    Add these variables to the .env file (replace placeholder values):

    SUPABASE_URL=your_supabase_url
    SUPABASE_KEY=your_supabase_key
    SUPABASE_BUCKET=your_supabase_bucket
    SUPABASE_AUTH_JWKS_URL=your_jwks_url
    SUPABASE_PROJECT_ID=your_project_id
    
    DATABASE_URL=your_database_connection_string
    
    RAZORPAY_KEY_ID=your_razorpay_key_id
    RAZORPAY_KEY_SECRET=your_razorpay_secret

3. **Install Conda dependencies:**
    conda env create -f environment.yml

4. **Activate the Conda environment:**
    conda activate virtspace

## RUNNING THE APPLICATION:

Step 1: **Start Celery Worker (in a new terminal window):**

    celery -A app.celery.celeryapp worker --loglevel=info

Step 2: **Start FastAPI Server:**
    uvicorn app.main:app --reload

The application will run at: http://localhost:8000

