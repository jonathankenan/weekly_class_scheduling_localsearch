# Tugas Besar 1 IF3170 – Artificial Intelligence  
## Weekly Class Scheduling Using Local Search

### Team Information  
**Team Name:** ngermnkibols  

| Name | Student ID |
|------|-------------|
| Sebastian Enrico Nathanael | 13523134 |
| Jonathan Kenan Budianto | 13523139 |
| Mahesa Fadhillah Andre | 13523140 |

---

### Program Description  
This project is developed as part of the IF3170 Artificial Intelligence course.  
The program implements **local search algorithms** to find an optimal or near-optimal weekly class schedule that minimizes conflicts between courses, students, and rooms.  

The implementation follows the given specification and includes:  
- Problem representation for weekly class scheduling  
- State generation and modification (neighbor moves)  
- Multiple local search algorithms to optimize the schedule  
- Visualization of experiment results and schedule outcomes  

---

### Objectives and Benefits  
**Objective:**  
To apply and evaluate several local search algorithms in solving a real-world optimization problem — weekly course scheduling.  

**Benefits:**  
- Gain hands-on understanding of state-space search and local optimization  
- Compare the performance of different local search strategies  
- Strengthen skills in heuristic design and algorithm analysis  

---

### Technologies Used  
- **Language:** Python  
- **Visualization Library:** Matplotlib  

---

### Features  
| Feature | Description |
|----------|-------------|
| **Random Initialization** | Generates a random valid initial schedule |
| **Objective Function Evaluation** | Calculates penalties based on room and student conflicts |
| **Hill Climbing Algorithms** | Includes Steepest Ascent, Sideways Move, Stochastic, and Random Restart variants |
| **Simulated Annealing** | Allows probabilistic acceptance of worse states to escape local optima |
| **Genetic Algorithm** | Uses population-based search with crossover and mutation |
| **Visualization** | Plots objective function progress and displays the resulting schedule |

---

### How to Run  

#### 1. Move to the Root Directory  
```bash
cd <project-directory>
```
#### 2. Run the Main Program
```bash
python main.py
```

### Task Division
| Member                                    | Responsibilities                                                                                                                                                             |
| ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Mahesa Fadhillah Andre (13523140)**     | Base logic and schedule representation, Genetic Algorithm implementation, documentation, testing, main program                                                               |
| **Jonathan Kenan Budianto (13523139)**    | Hill Climbing variants (Steepest Ascent, Sideways Move, Stochastic, Random Restart), Simulated Annealing algorithm, objective function, documentation, testing, main program |
| **Sebastian Enrico Nathanael (13523134)** | Simulated Annealing implementation, documentation, testing                                                                                                                   |
