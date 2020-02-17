Partners:
	Shineng Tang and Yash Solanki

Search approach:
	-Simple A* for search (nothing too special there). 
Heuristic:
	-the axe tools are removed from search since they are not needed
	-already obtained tools are removed from search since they are not needed
	-if there's more of a consumable than its highest consumed recipe we remove getting it from search since we have enough for the time being
	