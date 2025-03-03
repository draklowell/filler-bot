# Filler bot
This is a project for the Fundamentals of Programming course. For details on the game, check the [Filler repo](https://github.com/vomnes/Filler). The algorithm's idea is to place peace as close to the enemy as possible.

## Usage
First of all, you have to make the bot script executable. For UNIX systems run the following command:
```bash
chmod +x bot.py
```
After that, you can use the bot in the game:
```bash
./filler_vm -p1 ./bot.py -p2 [player 2] -f [map]
```

## Algorithm
### What does "as close as possible" mean
Let's define the following "confidence" function:

$$f(P) = -\sum_{p\in P}\min\\{|p, q|: q\in Q\\}$$

Where $$Q$$ is a set of all enemy points and $$P$$ is a set of points that potentially will be placed. So the algorithm's goal is to find such $$P$$, which maximizes $$f(P)$$.

It does it by iterating over all possible $$P$$, evaluating for each confidence, and choosing the best one.

### Checking whether $$P$$ satisfies game rules
For this purpose `blit_figure` function is used. For each point $$p\in P$$ it checks whether there is an enemy point at that position. If there is, then we skip this arrangement $$P$$. Otherwise, if there is a point, that our bot has placed before, we store a flag. If it occurs again with the flag set, then this arrangement does not satisfy game rules.

### Evaluating $$\min\\{|p, q|: q\in Q\\}$$
For an effective yet simple evaluation of this value, we use "spiral search", which is generated by the `expanding_distance` function. Firstly algorithm searches for the point $$q_1\in Q$$ which satisfies $$|p, q_1|\_\infty$$, where $$|a, b|\_\infty$$ is Chebyshev distance between $$a$$ and $$b$$. If there is no such point, then continue for $$|p, q_2|\_\infty = 2$$ and so on.

At some point, the algorithm will either exit because of the iterations limit or find such point $$q_n$$, that $$|p, q_n|\_\infty = n$$. Then we evaluate $$|p, q_n|$$ (Euclidean distance) and continue looking for all points $$q\*\in Q\* \subset Q$$ that satisfy the following inequality:

$$|p, q_n|\_\infty \leq |p, q\*|\_\infty \leq |p, q_n|$$

And then for each point $$q* \in Q\*$$ we evaluate $$|p, q\*|$$ and choose the smallest one. In this way, we can find the smallest distance from $$p$$ to the set of enemy points $$Q$$.

Also, we cache this value to increase the efficiency of the program when iterating over a large number of possible $$P$$. This cache is invalidated at each game step.

## Place for improvements and optimization
Since this code is built for testing many different algorithms it is slightly overcomplicated. For example, we can get rid of figure blitting, instead of working with the actual set of points rather than "picture".
