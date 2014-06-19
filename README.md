hcc
===

b- and c-tagging + analysis

- The training script assumes that the input files are in the subdirectory "data/". On the UZH machine, we should probably set soft links.
- This was tested with 5.34.13, so it's hopefully at least as good in 5.34.18
- An sklearn training module will be added


Notes on optimisation:

- From experience, the trees with gradient boosting will outperform all other methods.
- Parameters that should be optmised are 'MaxDepth', 'Shrinkage', and 'NTrees'. The latter two will play against each other (lower shrinkage with more cuts gives a better performance, but increases the training time).
- A fairly good algorithm is to start with low shrinkange and high n(trees) to find the best MaxDepth, then optimise shrinkage and n(trees)
- The other parameters can be checked thereafter, but shouldn't lead to large changes of the results, though a lower GradBaggingFraction leads to better results in certain cases
