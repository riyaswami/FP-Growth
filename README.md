# FP-Growth

FP Growth for association mining

This python script works on transactional data to generate frequent item sets and visualise FP tree, also the conditional FP trees are created for frequen items.

Input format: -> Path to a text file having transactions line by line, all the items in a transaction is separated by a single space character.
			        -> minimum support
			        -> minimum confidence

Output: -> Frequent Itemsets, Association rules, FP tree, Conditional FP tree
		    -> The trees created will be stored in the location specified in the print_digraph() and print_digraph_cond_tree()

Libraries used: -> itertools    : to create all the subsets 
				        -> import os    : to check file path
				        -> import time  : to compute time taken
				        -> import graphviz  : to draw the tree
				        -> import threading  : to implement multithreading for visualising the trees created.
	
