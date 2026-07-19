import os

# Redirect HOME and cache directories to /tmp on Vercel serverless environment
try:
    if os.getenv("VERCEL") or not os.access(os.path.expanduser("~"), os.W_OK):
        os.environ["HOME"] = "/tmp"
        os.environ["TMPDIR"] = "/tmp"
        os.environ["HF_HOME"] = "/tmp/hf"
        os.environ["CHROMADB_CACHE_DIR"] = "/tmp/chroma"
        DB_DIR = "/tmp/chroma_db"
    else:
        DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")
except Exception:
    DB_DIR = "/tmp/chroma_db"

import chromadb

def get_chroma_client():
    return chromadb.PersistentClient(path=DB_DIR)

def init_vector_store():
    client = get_chroma_client()
    collection = client.get_or_create_collection(name="sports_facts")
    
    # Check if collection is empty
    if collection.count() == 0:
        print("Seeding sports facts database...")
        seed_data = [
            # Cricket
            {"id": "c1", "sport": "Cricket", "difficulty": "Easy", "text": "The first-ever official international cricket match was played in 1844 between the United States and Canada in New York."},
            {"id": "c2", "sport": "Cricket", "difficulty": "Medium", "text": "Sachin Tendulkar scored his 100th international century against Bangladesh in March 2012 at the Sher-e-Bangla National Cricket Stadium in Mirpur."},
            {"id": "c3", "sport": "Cricket", "difficulty": "Medium", "text": "In 1999, Anil Kumble became only the second bowler in Test cricket history to take all ten wickets in a single innings, achieving this feat against Pakistan at the Feroz Shah Kotla in Delhi."},
            {"id": "c4", "sport": "Cricket", "difficulty": "Easy", "text": "The highest individual score in Test cricket history is 400 not out, scored by Brian Lara of the West Indies against England in Antigua in 2004."},
            {"id": "c5", "sport": "Cricket", "difficulty": "Medium", "text": "In the 1983 Cricket World Cup final, India defeated the West Indies by 43 runs at Lord's, defending a low score of 183 to win their first World Cup."},
            # Football
            {"id": "f1", "sport": "Football", "difficulty": "Easy", "text": "The first FIFA World Cup was held in 1930 in Uruguay, and the host nation Uruguay won the tournament by defeating Argentina in the final."},
            {"id": "f2", "sport": "Football", "difficulty": "Easy", "text": "Lionel Messi has won the Ballon d'Or a record 8 times as of 2023, more than any other football player in history."},
            {"id": "f3", "sport": "Football", "difficulty": "Easy", "text": "In the 2014 FIFA World Cup, Germany defeated the host nation Brazil by an astonishing scoreline of 7-1 in the semi-final match."},
            {"id": "f4", "sport": "Football", "difficulty": "Medium", "text": "Real Madrid won five consecutive European Cup titles from 1956 to 1960, a record that remains unmatched in UEFA Champions League history."},
            {"id": "f5", "sport": "Football", "difficulty": "Hard", "text": "The fastest goal in FIFA World Cup history was scored by Hakan Sükür of Turkey in just 11 seconds against South Korea in the 2002 third-place match."},
            {"id": "f6", "sport": "Football", "difficulty": "Medium", "text": "Leicester City won the English Premier League in the 2015-2016 season under manager Claudio Ranieri, starting the season with 5000-to-1 odds."},
            # Badminton
            {"id": "b1", "sport": "Badminton", "difficulty": "Medium", "text": "India won its first-ever Thomas Cup title in 2022 by defeating the 14-time champions Indonesia 3-0 in the final held in Bangkok, Thailand."},
            {"id": "b2", "sport": "Badminton", "difficulty": "Medium", "text": "Prakash Padukone was the first Indian badminton player to win the prestigious All England Open Badminton Championships, achieving this feat in 1980."},
            {"id": "b3", "sport": "Badminton", "difficulty": "Easy", "text": "Badminton made its official debut as a full medal sport at the Summer Olympic Games in 1992 in Barcelona, Spain."},
            {"id": "b4", "sport": "Badminton", "difficulty": "Medium", "text": "Carolina Marin of Spain became the first non-Asian female badminton player to win an Olympic gold medal in singles, winning at the 2016 Rio Olympics."},
            {"id": "b5", "sport": "Badminton", "difficulty": "Hard", "text": "The fastest badminton smash on record in a tournament was hit by Satwiksairaj Rankireddy of India, reaching an incredible speed of 565 km/h (351 mph) in 2023."},
            # Tennis
            {"id": "t1", "sport": "Tennis", "difficulty": "Easy", "text": "Rafael Nadal has won the French Open (Roland Garros) a record 14 times, making him the most dominant player on clay courts in tennis history."},
            {"id": "t2", "sport": "Tennis", "difficulty": "Medium", "text": "Roger Federer won five consecutive US Open titles from 2004 to 2008, a record in the Open Era."},
            {"id": "t3", "sport": "Tennis", "difficulty": "Hard", "text": "The longest tennis match in history was played at Wimbledon in 2010 between John Isner and Nicolas Mahut, lasting 11 hours and 5 minutes over three days."},
            {"id": "t4", "sport": "Tennis", "difficulty": "Hard", "text": "Steffi Graf is the only tennis player in history to win a Golden Slam, winning all four Grand Slam singles titles and the Olympic gold medal in the same calendar year (1988)."},
            {"id": "t5", "sport": "Tennis", "difficulty": "Easy", "text": "Serena Williams has won 23 Grand Slam singles titles in the Open Era, the most by any player, male or female, in this era."},
            # Basketball
            {"id": "ba1", "sport": "Basketball", "difficulty": "Easy", "text": "The Boston Celtics and the Los Angeles Lakers are tied for the most NBA championships in history, each having won 17 titles."},
            {"id": "ba2", "sport": "Basketball", "difficulty": "Medium", "text": "Wilt Chamberlain holds the record for the most points scored in a single NBA game, scoring 100 points for the Philadelphia Warriors against the New York Knicks in 1962."},
            {"id": "ba3", "sport": "Basketball", "difficulty": "Easy", "text": "Michael Jordan won six NBA championships with the Chicago Bulls, winning the Finals MVP award in all six championship series (1991-1993, 1996-1998)."},
            {"id": "ba4", "sport": "Basketball", "difficulty": "Easy", "text": "The Golden State Warriors set the record for the most regular-season wins in NBA history during the 2015-16 season, finishing with a 73-9 record."},
            {"id": "ba5", "sport": "Basketball", "difficulty": "Medium", "text": "Kareem Abdul-Jabbar's signature shot, the 'Skyhook', was widely regarded as one of the most unstoppable shots in basketball history, helping him score 38,387 career points."}
        ]
        
        ids = [item["id"] for item in seed_data]
        documents = [item["text"] for item in seed_data]
        metadatas = [{"sport": item["sport"], "difficulty": item["difficulty"]} for item in seed_data]
        
        collection.add(ids=ids, documents=documents, metadatas=metadatas)
        print(f"Successfully seeded {len(seed_data)} sports facts!")
    else:
        print(f"Database already populated with {collection.count()} facts.")

def query_sports_facts(sport: str, difficulty: str = None, n_results: int = 5):
    try:
        client = get_chroma_client()
        collection = client.get_or_create_collection(name="sports_facts")
        
        # Ensure collection is seeded if count is 0
        if collection.count() == 0:
            init_vector_store()
            
        # Perform metadata retrieval (requires NO ONNX embedding model download)
        results = collection.get(
            where={"sport": sport},
            limit=n_results
        )
        
        retrieved = []
        if results and results.get("documents") and len(results["documents"]) > 0:
            for doc, meta in zip(results["documents"], results["metadatas"]):
                retrieved.append({
                    "text": doc,
                    "sport": meta.get("sport", sport),
                    "difficulty": meta.get("difficulty", difficulty or "Medium")
                })
        return retrieved
    except Exception as e:
        print(f"ChromaDB retrieval notice: {e}")
        return []

if __name__ == "__main__":
    init_vector_store()
    print("Test Query (Cricket):")
    res = query_sports_facts("Cricket", "Medium")
    for r in res:
        print(f"- [{r['difficulty']}] {r['text']}")
