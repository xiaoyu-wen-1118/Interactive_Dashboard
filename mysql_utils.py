import sqlalchemy as sa
from sqlalchemy import create_engine
import pandas as pd

def connector():
    cnxn = create_engine("mysql+mysqldb://xiaoyu:cs411uiuc@localhost:3306/academicworld")
    return cnxn

def get_topProfessor(keyword_1, keyword_2):
    cnxn = connector()
    data = pd.read_sql(
        """
        SELECT f.name as 'Professor', ROUND(SUM(p.num_citations * pk.score),2) AS KRC, f.id
        FROM faculty f
        JOIN faculty_publication fp ON f.id = fp.faculty_id
        JOIN publication p ON fp.publication_id = p.id
        JOIN publication_keyword pk ON p.id = pk.publication_id
        JOIN keyword k ON pk.keyword_id = k.id
        WHERE k.name = %(k1)s OR k.name = %(k2)s 
        GROUP BY f.id, f.name
        ORDER BY KRC DESC
        LIMIT 10;
        """, params={"k1": keyword_1, "k2": keyword_2}, con = cnxn)
    return data

def get_selectProf(selected_prof_id):
    cnxn = connector()
    data = pd.read_sql(
    """
    SELECT f.name AS 'Prof_name', f.research_interest, f.photo_url, f.email, f.phone, u.name AS 'Affiliation'
    FROM faculty f
    JOIN university u ON f.university_id = u.id
    WHERE f.id = %(prof_id)s
    """, params={"prof_id": selected_prof_id}, con = cnxn)
    return data

def prof_top10Publication(selected_prof_id, keyword_1, keyword_2):
    cnxn = connector()
    data = pd.read_sql(
    """
    SELECT p.title, p.year, k.name AS 'keyword', p.num_citations AS 'CITED BY'
    FROM faculty f
    JOIN faculty_publication fp ON f.id = fp.faculty_id
    JOIN publication p ON fp.publication_id = p.id
    JOIN publication_keyword pk ON p.id = pk.publication_id
    JOIN keyword k ON pk.keyword_id = k.id
    WHERE (k.name = %(k1)s OR k.name = %(k2)s) AND f.id = %(prof_id)s
    ORDER BY p.num_citations DESC
    LIMIT 10
    """, params={"prof_id": selected_prof_id, "k1": keyword_1, "k2": keyword_2}, con = cnxn)
    return data

def write_prof_tosql(favorite_prof_df):
    cnxn = connector()
    data = pd.read_sql(
    """
    SELECT * FROM user_favorite_prof
    """, con=cnxn)
    dup = favorite_prof_df.merge(data, how = 'inner', indicator=False)

    if len(dup) != 0:
        print("Already added!")
        print(dup)
    else:
        favorite_prof_df.to_sql('user_favorite_prof', con=cnxn, if_exists='append', index=False)

def write_school_tosql(favorite_school_df):
    cnxn = connector()
    data = pd.read_sql(
    """
    SELECT * FROM user_favorite_university
    """, con=cnxn)
    dup = favorite_school_df.merge(data, how = 'inner', indicator=False)

    if len(dup) != 0:
        print("Already added!")
        print(dup)
    else:
        favorite_school_df.to_sql('user_favorite_university', con=cnxn, if_exists='append', index=False)

def delete_prof_fromsql(del_prof_df):
    # https://stackoverflow.com/questions/57761954/delete-rows-from-sql-server-bases-on-content-in-dataframe
    cnxn = connector()
    meta = sa.MetaData()

    # Map the target table in the db to a SQLAlchemy object
    user_favorite_prof = sa.Table('user_favorite_prof', meta, autoload=True, autoload_with=cnxn)

    cond = del_prof_df.apply(lambda row: sa.and_(user_favorite_prof.c['Professor'] == row['Professor'],
                                        user_favorite_prof.c['Keyword1'] == row['Keyword1'],
                                        user_favorite_prof.c['Keyword2'] == row['Keyword2']), axis=1)
    cond = sa.or_(*cond)

    delete = user_favorite_prof.delete().where(cond)
    with cnxn.connect() as conn:
        conn.execute(delete)
def delete_school_fromsql(del_school_df):
    cnxn = connector()
    meta = sa.MetaData()

    # Map the target table in the db to a SQLAlchemy object
    user_favorite_school = sa.Table('user_favorite_university', meta, autoload=True, autoload_with=cnxn)

    cond = del_school_df.apply(lambda row: sa.and_(user_favorite_school.c['University'] == row['University'],
                                        user_favorite_school.c['Keyword1'] == row['Keyword1'],
                                        user_favorite_school.c['Keyword2'] == row['Keyword2']), axis=1)
    cond = sa.or_(*cond)

    delete = user_favorite_school.delete().where(cond)
    with cnxn.connect() as conn:
        conn.execute(delete)

def get_favorite_prof():
    cnxn = connector()
    data = pd.read_sql(
    """
    SELECT * FROM user_favorite_prof
    """, con=cnxn)

    return data

def get_favorite_school():
    cnxn = connector()
    data = pd.read_sql(
    """
    SELECT * FROM user_favorite_university
    """, con=cnxn)

    return data