## <center><u>RULES:</u>

#### <center>*1. GENOME*

* Each cell has it's own genome in form of a list containing:

```c
        TYPE                    GENOME
        -----                   ------
        int                     ID
        enum Status             STATUS
        float                   IMMUNITY
        enum Behaviour          BEHAVIOUR
        int                     FAMILY ID
        struct Coordinates      HOUSE
        struct Coordinates      JOB
        int                     AGE

        DEBUG:
        struct Coordinates      COORDINATES
        int                     DATE OF INFECTION
        int                     INCUBATION DURATION
        int                     INFECTION DURATION
        float                   PENALTIES
        float                   REWARDS
        int                     DATE OF DEATH
```
#### <center>*2. IMMUNITY*

* Each cell has it's own base immunity which is being randomized at start.
* Afterwarts immunity calculated by rule: 

![Rule](https://latex.codecogs.com/png.image?\dpi{110}%20B*\frac{2.5}{\sqrt{2\pi}}e^{-\left(2x-1\right)^{2}}%20+%20\sum%20R%20-%20\sum%20P)
where: ![Rule](https://latex.codecogs.com/png.image?\dpi{110}%20B) - base immunity, ![Rule](https://latex.codecogs.com/png.image?\dpi{110}%20A) - age, ![Rule](https://latex.codecogs.com/png.image?\dpi{110}%20R) - immunity rewards, ![Rule](https://latex.codecogs.com/png.image?\dpi{110}%20P)- immunity penalties  


#### <center>*3. PHASES*

```c
        STATUS:         
        -------         
        not_infected    
        vaccinated      
        incubation      
        infected        
        recovered       
        dead            
```

**2.1) INCUBATION**

* Some percent of cells get infected during 1st generation
* Their incubation duration is calculated by the rule: 

```c
        incubation = (l_bound + (l_bound - u_bound)) * cos(immunity)
```
* During incubation cells have lower chance of infecting the others
* Immunity penalty raises during that peroid


**2.2) INFECTION**

* After incubation phase cell gets completely infected
* Duration of infection phase is being calculated by the rule: 

```c
        infection = (l_bound + (l_bound - u_bound)) * sin(immunity)
```
* From now on it has a higher chance of infecting other cells and a risk of dying
* Chance of dying is calculated by the rule: 

```c
        chance = cos(self.calc_immunity(i, j)) ** 5
```
* Immunity penalty lowers during that peroid

**2.3) RECOVERY**

* Once recovered, cell gets immunity reward, but it's still posible for cell to get sick again

**2.4) VACCINATION**

* All cell are unvaccinated at the beginning
* Chance of vaccination starts at 5% and raises by the rule
```c
        vac_attractiveness = vac_base_attractiveness * death_count
```

* Vaccinated cells have an immunity reward so chance of getting infected is lower 


**2.5) DEATH**

* After dying cell becomes inactive for 3 generations
* After that, cell dissapears


#### <center>*4. BEHAVIOUR*

* Each cell has it's own behavoiur. All behaviour types are listed in a table:

```c
        VALUE       BEHAVIOUR   
        -----       ---------
        0           RANDOM
        1           HEADING HOME
        2           HEADING TO WORK
```

* Behavior is represented in the way of a list containing:

```c
        behaviour = [type; path; <bool> reached]
```

* Random behaviour means that cell is randomly roaming around. It may be canceled at any time
* Other types of behaviour needs to be marked to be "done", and cannot be interrupted.

#### <center>*5. MISC*
* Every iteration equals 1/4 of a day