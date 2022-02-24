## <center><u>RULES:</u>

#### <center>*1. GENOME*

* Each cell has it's own genome in form of a list containing:

```python
        INDEX   GENOME
        -----   ------
        0       STATUS
        1       IMMUNITY
        2       BEHAVIOUR
        3       DATE OF INFECTION
        4       INCUBATION DURATION
        5       INFECTION DURATION
        6       PENALTIES
        7       REWARDS
        8       FAMILY 
        9       DATE OF DEATH
        10      HOUSE
        11      WORK
        12      AGE
```

#### <center>*2. PHASES*

```python
        STATUS:         VALUE       
        -------         -----
        not infected    1  
        vaccinated      2
        incubation      4 
        infected        5
        recovered       -1
        dead            -2 
        empty           None 
```

**2.1) INCUBATION**

* Some percent of cells get infected during 1st generation
* Their incubation duration is calculated by the rule: 

```python
        incubation = (l_bound + (l_bound - u_bound)) * cos(immunity)
```
* During incubation cells have lower chance of infecting the others
* Immunity penalty raises during that peroid


**2.2) INFECTION**

* After incubation phase cell gets completely infected
* Duration of infection phase is being calculated by the rule: 

```python
        infection = (l_bound + (l_bound - u_bound)) * sin(immunity)
```
* From now on it has a higher chance of infecting other cells and a risk of dying
* Chance of dying is calculated by the rule: 

```python
        chance = cos(self.calc_immunity(i, j)) ** 5
```
* Immunity penalty lowers during that peroid

**2.3) RECOVERY**

* Once recovered, cell gets immunity reward, but it's still posible for cell to get sick again

**2.4) VACCINATION**

* All cell are unvaccinated at the beginning
* Chance of vaccination starts at 5% and raises by the rule
```python
        vac_attractiveness = vac_base_attractiveness * death_count
```

* Vaccinated cells have an immunity reward so chance of getting infected is lower 


**2.5) DEATH**

* After dying cell becomes inactive for 3 generations
* After that, cell dissapears


#### <center>*2. BEHAVIOUR*

* Each cell has it's own behavoiur. All behaviour types are listed in a table:

```python
        VALUE       BEHAVIOUR   
        -----       ---------
        0           RANDOM
        1           HEADING HOME
        2           HEADING TO WORK
```

* Behavior is represented in the way of a list containing:

```python
        behaviour = [type; path; <bool> reached]
```

* Random behaviour means that cell is randomly roaming around. It may be canceled at any time
* Other types of behaviour needs to be marked to be "done", and cannot be interrupted.