# Interactive Family Tree

This project is for creating and managing family trees interactively.

## Project Structure

```
im-family-tree/
├── README.md
└── src/         # Source code directory
```

## Project Overview

# Family Tree Visualization

An interactive web application for creating and visualizing family relationships with a clean, intuitive interface.

## Features

- **Person Management**
  - Add new family members
  - Interactive node dragging
  - Automatic generation level assignment

- **Relationship Types**
  - Parent-Child relationships (vertical positioning)
  - Spouse relationships (with heart symbol )

- **Dynamic Visualization**
  - Force-directed graph layout
  - Generation-based hierarchy
  - Responsive design with window resizing
  - Smooth animations
  - Clear relationship indicators

## Technology Stack

- **Backend**: Python with Flask
- **Database**: SQLAlchemy (SQLite)
- **Frontend**: HTML, JavaScript with D3.js
- **Visualization**: D3.js force layout

## Getting Started

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python app.py
   ```

3. **Access the Application**
   - Open your browser and navigate to `http://localhost:3333`

## Usage

1. **Adding People**
   - Enter a name in the "Add Person" form
   - Click "Add" to create a new family member

2. **Creating Relationships**
   - Select relationship type (Parent-Child or Spouse)
   - Choose the people to connect
   - Click "Add Relationship" to establish the connection

3. **Interacting with the Visualization**
   - Drag nodes to adjust positions
   - Nodes will maintain their generation level
   - Window resizing automatically adjusts the layout

## Design Principles

- **Clean Interface**: Minimalist design focusing on clarity
- **Intuitive Interaction**: Simple forms and natural dragging behavior
- **Clear Hierarchy**: Parents positioned above children
- **Visual Relationships**: 
  - Parent-Child: Vertical positioning
  - Spouse: Black line with heart icon

## Dependencies

- Flask==2.3.3
- Flask-SQLAlchemy==3.1.1
- SQLAlchemy==2.0.21

## Development

The application is built with a focus on:
- Modular design
- Responsive visualization
- Clean code principles
- Error handling
- User experience

## Future Enhancements

- User authentication
- Data import/export
- Advanced relationship types
- Photo uploads
- Family tree sharing
