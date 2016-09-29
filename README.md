## betting-strategy
# Betting-Strategy
a simulation of betting in a sccoer game

brain storming is highly encouraged here about offering your betting strategy

欢迎各位小伙伴开开脑洞，提出你的下注策略

## Module Introduction
1. LoadData: Read original data from db(MySQL currently, It can be changed in the future. e.g. Redis, HBase... you name it)
2. Strategy: Specific Strategy is defined here, inheriting from Strategy class
3. Analysis: This part is a little coupled with Strategy module, cause the data to be analyzed is grenerated in Strategy. Anyway, we use elastic-search to analyze operation data and it also can be replaced by other analytic tools(e.g. SQL...)

#### for more detail, please see [wiki](https://github.com/xiaoyao2102/betting-strategy/wiki) 
