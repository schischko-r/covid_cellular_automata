## <u>RULES:</u>

#### *1. GENOME*

* Each cell has it's own genome in form of a list containing:

        INDEX   GENOME                          STATUS:         VALUE       
        -----   ------                          -------         -----
        0       STATUS                          not infected    1  
        1       IMMUNITY                        vaccinated      2
        2       BEHAVIOUR                       incubation      4 
        3       DATE OF INFECTION               infected        5
        4       INCUBATION DURATION             recovered       -1
        5       INFECTION DURATION              dead            -2 
        6       PENALTIES                       empty           None 
        7       REWARDS                         
        8       FAMILY 
        9       DATE OF DEATH                         


#### *2. PHASES*

**2.1) INCUBATION**

* Some percent of cells get infected during 1st generation
* Their incubation duration is calculated by the rule: 

```
    incubation = (l_bound + (l_bound - u_bound)) * cos(immunity)
```
* During incubation cells have lower chance of infecting the others
* Immunity penalty raises during that peroid


**2.2) INFECTION**

* After incubation phase cell gets completely infected
* Duration of infection phase is being calculated by the rule: 

```
    infection = (l_bound + (l_bound - u_bound)) * sin(immunity)
```
* From now on it has a higher chance of infecting other cells and a risk of dying
* Chance of dying is calculated by the rule: 

```
    chance = cos(self.calc_immunity(i, j)) ** 5
```
* Immunity penalty lowers during that peroid

**2.3) RECOVERY**

* Once recovered, cell gets immunity reward, but it's still posible for cell to get sick again

**2.4) VACCINATION**

* All cell are unvaccinated at the beginning
* Chance of vaccination starts at 5% and raises by the rule
```
    vac_attractiveness = vac_base_attractiveness * death_count
```

* Vaccinated cells have an immunity reward so chance of getting infected is lower 


**2.5) DEATH**

* After dying cell becomes inactive for 3 generations
* After that, cell dissapears


