

# Toolkit of Discovering Graduate School and Advisor


## 1.	Purpose: 

When college students reach the point of contemplating furthering their studies and research, they often face difficult decisions and a multitude of questions. The main questions are: 

* **What are the current trending topics in the field of study of the students?**
* **Which universities are most relevant to these topics?** 
* **Who are the most productive professors in these fields of study?**
* **What papers have these professors published in these fields of study?**
* **With which other professors do these professors collaborate?**

Our application aims to utilize our academic dataset to explore and provide answer to the above questions easily. The widgets are arranged in a logical order, allowing users to begin their search with their questions in mind. As they scroll down the website, the answers to their questions become increasingly clear. In the end, users can choose to save their search results in the application for future reference.

![dashboard_demo](https://github.com/xiaoyu-wen-1118/Interactive_Dashboard/blob/main/dashboard_demo.png)

The **"keyword"** feature in our dataset serves as the main input for our application as it connects both *faculty* table and *publication* table in the dataset. We use **Plotly Dash** as our front-end and different types of databases such as **MySQL, MongoDB,** and **Neo4j** as our back-end. We create **seven** widgets, including two **updating widgets** and two pairs of **multi-database querying widgets**.


## 2.	Demo: 
https://mediaspace.illinois.edu/media/t/1_si5e6il9

## 3.	Installation: 

Here are python libraries that need to be installed before using: 

`pandas`, `dash`, `dash_bootstrap_componetns`, `plotly`, `dash_extensions.enrich`, `neo4j`, `networkX`, `sqlalchemy`, `pymongo`
   
We recommend using "pip install" to install `NetworkX`, as there may be version conflicts when using the library with "conda install". Since only the given databases are used, no other installations are necessary.

## 4.	Design:

### 4.1	Idea Design:

Since our scenario is assisting students in finding their graduate school and advisor, we attempt to utilize the natural thought process that a user goes through when searching for what they need. Here is a sketch of the user’s process.

![Idea Design](https://github.com/xiaoyu-wen-1118/Interactive_Dashboard/blob/main/idea_design.jpg)

### 4.2	 Layout Design: 

Our aim is to guide users through the website, from top to bottom. 

The website's **navigation bar** is straightforward for users who know what they are looking for. They can select up to two keywords at a time, which will generate results in two widgets: **"Top10 Professors"** and **"Top10 Universities"**. These widgets display the most crucial information that students consider when selecting a graduate school.

The top-left widget enables users to explore the most popular topics in recent years. We use a **drop-down menu** with options for 1 year, 3 years, and 5 years, and display the results using a **Treemap visualization** for its vivid and intuitive nature. Users can manually select their preferred keywords and then return to the navigation bar to search for results regarding professors and universities.

The second row of the website displays information on the selected professor. On the left-hand side is **“Professor info”** widget; users can find the professor's name, affiliated university, contact information, and publications, sorted in descending order by citation count. On the right-hand side is **“Collaboration network”** widget; users can view the collaboration network of the selected professor in a graph format. By pointing the mouse to a node in the graph, users can view the collaborator's name.

The third row of the website is dedicated to saved data. Users can use the **"add to favorite"** button in the **"Top10 Professors"** and **"Top10 Universities"** widgets to select multiple favorite professors and universities and save them for future reference in their respective categories. Users can delete the saved data manually though the “delete” button.

###    4.3	Further Improvement:

Although the current user interface is functional with its basic colors and graphs, we recognize that there is room for improvement in terms of its visual appeal. Due to time constraints, we had to prioritize clarity and simplicity, but we are open to exploring other tools available in Dash to enhance the interface's aesthetics. 

We would like to expand the functionality of our application by incorporating additional widgets and data. For instance, we could include the locations of universities and even use a map to visualize the distribution of universities that are relevant to specific topics. We believe that this would greatly enhance the user experience and provide valuable insights to our users.

To allow for personalized user experiences and data storage, we would like to implement a log-in method that enables different users to save their individual results in the database. This will enhance the security of the application.

## 5.	Implementation: 

In order to provide a comprehensive and satisfying user experience that fully realizes our application's potential, we believe that seven widgets are an appropriate number to achieve our design goals and tells a complete story about our application design.

### 5.1	Dashboard:
We use **Dash Plotly** as our dashboard framework, the libraries are `dash`, `plotly`, `pandas`.

### 5.2 Website Style: 
The web has a navigation bar on the top where users can input at least two keywords and perform searching using the search button. Each widget is included in a dash bootstrap component card. The seven cards are arranged in 3 rows. The first row contains 3 columns with the same width. The second row contains a wider column for the ultra-wide card and a smaller column for the normally sized card. The third row contains 2 columns with the same width. A padding of 15px is used to make sure the contents won’t be too close to the browser borders.

### 5.3 Database access:

Here is a list of widgets and the database and libraries use:
| Widget Name | Database use | Type of Widget | Library Use|
|---|---|---|---|
|1|Top Keywords in Recent Years | mongoDB | Querying widget | pymongo, pandas |
|2| Top10 Professors on Selected Keywords | SQL | Querying widget | sqlalchemy, pandas |
|3| Top10 universities on selected keywords | mongoDB | Querying widget | Pymongo, pandas |
|4| Professor info |Sql|Querying widget|Sqlalchemy, pandas |
|5| Collaboration network |	Neo4j	| Querying widget |Neo4j, Pandas, networkX |
|6|Favorite professors | SQL|Updating widget | Sqlalchemy,Pandas |
|7| Favorite Universities | SQL |Updating widget | Sqlalchemy, pandas |
 

## 6.	Database Techniques: 

1. **Indexing**. We create indexes for faculty.id and keyword.name, because these two attributes are frequently used to filter the mySQL queries in WHERE clause. After creating indexes, the mySQL queries significantly speed up.
2. **View**. We create view in order to simplify the query and customize the perception of faculty - publication - keyword.
3. **Constraint**. We create two tables to save user's favorite professors and universities, and set constraints ‘Not Null’ for all attributes. In `mysql_utils.py`, we also set constraints to avoid duplicate tuples being written to the two tables of user's favorite professors and universities. 


### Brife explanation of the implementation of **“Collaboration network”** widget:

At first, we attempted to display the network graph generated from Neo4j directly on the dashboard, but this turned out to be unachievable. As an alternative, we tried downloading the Neo4j graph as a **.jpg** file and passing a local link to the dashboard. However, we were dissatisfied with the outcome, as we wanted users to be able to zoom in and click on nodes within the graph. Ultimately, we discovered the `networkX` library, which enabled them to use Neo4j to query the necessary data and generate a pandas dataframe. We then used the `pandas` dataframe to create a networkX graph and obtained X and Y coordinates for each node and edge. Finally, we used the coordinate data to generate the final graph using the `plotly.graph_objs` library. [Here is the link of reference article.](https://towardsdatascience.com/tutorial-network-visualization-basics-with-networkx-and-plotly-and-a-little-nlp-57c9bbb55bb9)

## 7.	Extra-Credit Capabilities: 

1. **Multi-database querying**. We use the combined outputs of keyword1 and keyword2 to query two widgets: the **"Top Professors"** widget, which utilizes SQL database as its backend, and the **"Top Universities"** widget, which utilizes MongoDB as its backend.

2. **Multi-database querying**. We utilize the output of the **"Top Professors"** widget to query widgets **"Professor Info"** and the **"Collaboration Network"**.

## 8.	Contributions: 

*	**Xiaoyu Wen**: 
Scenario design, user interface design, frontend coding, SQL backend coding, video recording, report writing.
Total hour use: 40hours.
*	**Wei Dai**: 
Scenario design, Mongodb backend coding, Neo4j backend coding, Report writing. 
Total hour use: 40 hours.

