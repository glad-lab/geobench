#!/bin/bash
set -e

echo "=================================================="
echo "Adversarial SEO Research - Environment Setup"
echo "=================================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed and running
echo -e "\n${YELLOW}Checking Docker installation...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is installed and running${NC}"

# Check if docker-compose is available
echo -e "\n${YELLOW}Checking Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    # Try docker compose (newer syntax)
    if ! docker compose version &> /dev/null; then
        echo -e "${RED}❌ Docker Compose is not available.${NC}"
        exit 1
    else
        COMPOSE_CMD="docker compose"
    fi
else
    COMPOSE_CMD="docker-compose"
fi

echo -e "${GREEN}✅ Docker Compose is available${NC}"

# Check if .env exists, create from template if not
echo -e "\n${YELLOW}Setting up environment configuration...${NC}"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo -e "${GREEN}✅ Created .env file${NC}"
        echo -e "${YELLOW}⚠️  Please edit .env and add your API keys!${NC}"
    else
        echo -e "${RED}❌ .env.example not found. Cannot create .env file.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ .env file exists${NC}"
fi

# Validate Docker configuration
echo -e "\n${YELLOW}Validating Docker configuration...${NC}"
if $COMPOSE_CMD config --quiet; then
    echo -e "${GREEN}✅ Docker Compose configuration is valid${NC}"
else
    echo -e "${RED}❌ Docker Compose configuration has errors${NC}"
    exit 1
fi

# Create necessary directories
echo -e "\n${YELLOW}Creating directories...${NC}"
mkdir -p data/results logs qdrant_storage
echo -e "${GREEN}✅ Directories created${NC}"

# Check if API keys are configured
echo -e "\n${YELLOW}Checking API key configuration...${NC}"
source .env

if [[ "$API_PROVIDER" == "openai" ]]; then
    if [[ "$OPENAI_API_KEY" == "your_openai_api_key_here" || -z "$OPENAI_API_KEY" ]]; then
        echo -e "${RED}❌ OpenAI API key not configured${NC}"
        echo "Please edit .env and set your OPENAI_API_KEY"
        API_KEYS_NEEDED=true
    else
        echo -e "${GREEN}✅ OpenAI API key is configured${NC}"
    fi
elif [[ "$API_PROVIDER" == "llama" ]]; then
    if [[ "$LLAMA_API_KEY" == "your_llama_api_key_here" || -z "$LLAMA_API_KEY" ]]; then
        echo -e "${RED}❌ LLaMA API key not configured${NC}"
        echo "Please edit .env and set your LLAMA_API_KEY"
        API_KEYS_NEEDED=true
    else
        echo -e "${GREEN}✅ LLaMA API key is configured${NC}"
    fi
fi

# Final instructions
echo -e "\n${GREEN}=================================================="
echo -e "✅ SETUP COMPLETE!"
echo -e "==================================================${NC}"

if [[ "$API_KEYS_NEEDED" == "true" ]]; then
    echo -e "\n${YELLOW}NEXT STEPS:${NC}"
    echo "1. Edit the .env file and add your API keys"
    echo "2. Run the validation script: python scripts/validate_config.py"
    echo "3. Start the system: $COMPOSE_CMD up"
    echo "4. Open Jupyter Lab: http://localhost:8888"
    echo "5. Run the reproduction notebook"
else
    echo -e "\n${YELLOW}READY TO START:${NC}"
    echo "1. Validate configuration: python scripts/validate_config.py"
    echo "2. Start the system: $COMPOSE_CMD up"
    echo "3. Open Jupyter Lab: http://localhost:8888"
    echo "4. Run the reproduction notebook"
fi

echo -e "\n${YELLOW}HELPFUL COMMANDS:${NC}"
echo "• Validate config: python scripts/validate_config.py"
echo "• Start services: $COMPOSE_CMD up"
echo "• Stop services: $COMPOSE_CMD down"
echo "• View logs: $COMPOSE_CMD logs -f"
echo "• Clean restart: $COMPOSE_CMD down && $COMPOSE_CMD up"

echo -e "\n${YELLOW}DOCUMENTATION:${NC}"
echo "• Environment setup: docs/environment_setup.md"
echo "• Docker setup: SETUP.md"
echo "• Technical details: TECHNICAL.md"

echo -e "\n${GREEN}Happy researching! 🚀${NC}"