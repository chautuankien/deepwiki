## Deepwiki Agent

An AI-powered agent that automatically creates beautiful, interactive wikis for any codebase using Deepseek Coder and LangGraph.

### Features

🔍 **Intelligent Code Analysis:** Deep understanding of code structure, dependencies, and patterns
📚 **Comprehensive Documentation:** Automatic generation of API docs, guides, and examples
🎨 **Visual Diagrams:** UML diagrams for system architecture and pipelines
🤖 **Deep Research Chat:** Multi-turn conversations about your codebase
🚀 **Local Privacy:** Run entirely on your machine with Deepseek Coder
⚡ **Async Processing:** Fast, parallel analysis of large codebases

### Architecture
The agent uses LangGraph to orchestrate multiple specialized components:

>Repository → Fetch → Parse → Analyze → Document → Diagram → Wiki

### Project Structure
```bash
├── deepwiki
│   ├── config.py
│   ├── models      # Model and Prompt Creation
│   ├── rag         # RAG implementation
│   ├── tools       # Tools for agent
│   └── workflow    # Langgraph agent
```
