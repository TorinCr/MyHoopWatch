import sys
#from app.services.kenpom_session import kenpom_browser
import kenpompy.summary as kp
import pandas as pd
from kenpompy.utils import login
from bs4 import BeautifulSoup

KENPOM_EMAIL = ""
KENPOM_PASSWORD = ""
kenpom_browser = login(KENPOM_EMAIL, KENPOM_PASSWORD)

metrics = {
    "ortg": "ORtg",    
    "min": "Min",      
    "efg": "eFG",      
    "poss": "Poss",    
    "shots": "Shots",  
    "or": "OR",        
    "dr": "DR",        
    "to": "TO",        
    "arate": "ARate",  
    "blk": "Blk",      
    "ftrate": "FTRate", 
    "stl": "Stl",     
    "ts": "TS",        
    "fc40": "FC40",
    "fd40": "FD40",
}

# These need special handling due to library bugs
problematic_stats = {
    "2p": "2P",        
    "3p": "3P",        
    "ft": "FT",
}

stat_leaders = {}

def get_player_descriptions():

    player_descriptions = {
    "cooper_flagg_duke_": "The consensus #1 NBA Draft pick who delivered the most dominant freshman season in recent memory. Flagg averaged 19.2 points, 7.5 rebounds, and 4.2 assists while shooting 48.1% from the field and 38.5% from three. His 42-point explosion against Notre Dame set new freshman scoring records for both Duke and the ACC, showcasing elite versatility as a 6'9\" forward who can handle, shoot, and defend multiple positions.",
    "johni_broome_auburn": "Different unique description...",
    "mark_sears_alabama": "Another unique description...",
    }
    
    return player_descriptions
    

def handle_problematic_stat_scraping(browser, metric):
    """Handle stats that need web scraping"""
    print(f"Starting web scraping for {metric}...")
    
    # Fixed URLs for player stats - using correct parameters
    metric_urls = {
        "2P": "https://kenpom.com/playerstats.php?s=FG2Pct",
        "3P": "https://kenpom.com/playerstats.php?s=FG3Pct",
        "FT": "https://kenpom.com/playerstats.php?s=FTPct"
    }
    
    if metric not in metric_urls:
        raise Exception(f"No workaround available for {metric}")
        
    # Get the page content
    try:
        response = browser.get(metric_urls[metric])
        print(f"Got response {response.status_code} for {metric}")
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch {metric} page: {response.status_code}")
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Debug: Let's see what we're actually getting
        print(f"Page title: {soup.title.string if soup.title else 'No title'}")
        
        # Find the table - try multiple approaches
        table = None
        
        # Try ID first
        table = soup.find('table', {'id': 'playerstats-table'})
        if not table:
            # Look for tables that contain "Player" in the header
            tables = soup.find_all('table')
            print(f"Found {len(tables)} tables on the page")
            
            for i, t in enumerate(tables):
                # Check if this table has player data
                first_row = t.find('tr')
                if first_row:
                    cells = first_row.find_all(['th', 'td'])
                    row_text = [cell.get_text().strip() for cell in cells]
                    print(f"Table {i} first row: {row_text[:5]}...")  # Show first 5 cells
                    
                    if any('Player' in str(cell) for cell in row_text):
                        table = t
                        print(f"Using table {i} (contains 'Player')")
                        break
                        
        if not table and tables:
            table = tables[0]  # Fallback to first table
            print("Falling back to first table")
            
        if not table:
            raise Exception(f"No table found for {metric}")
        
        print(f"Using table for {metric}")
        
        # Extract data
        rows = []
        headers = None
        
        # Get headers - be more careful about finding the right header row
        header_row = None
        all_rows = table.find_all('tr')
        
        for i, row in enumerate(all_rows):
            cells = row.find_all(['th', 'td'])
            cell_texts = [cell.get_text().strip() for cell in cells]
            
            # Look for a row that contains "Player" 
            if any('Player' in text for text in cell_texts):
                header_row = row
                headers = cell_texts
                print(f"Found header row {i}: {headers}")
                break
        
        if not headers:
            # If no "Player" found, try first row as fallback
            if all_rows:
                first_row = all_rows[0]
                headers = [cell.get_text().strip() for cell in first_row.find_all(['th', 'td'])]
                header_row = first_row
                print(f"Using first row as headers: {headers}")
        
        if not headers:
            raise Exception(f"No headers found for {metric}")
            
        # Find the data rows (skip the header row)
        header_index = all_rows.index(header_row) if header_row in all_rows else 0
        data_rows = all_rows[header_index + 1:]
        
        print(f"Processing {len(data_rows)} data rows")
        
        for row_idx, row in enumerate(data_rows):
            cells = row.find_all(['td', 'th'])
            if len(cells) != len(headers):
                continue  # Skip rows that don't match header count
                
            row_data = []
            for i, cell in enumerate(cells):
                text = cell.get_text().strip()
                
                # Convert data types
                if i == 0:  # Rank column
                    try:
                        row_data.append(int(text) if text.isdigit() else None)
                    except:
                        row_data.append(None)
                elif headers[i] in ['Player', 'Team', 'Yr']:
                    row_data.append(text)
                elif headers[i] in ['Ht', 'Wt']:
                    row_data.append(text)
                else:
                    # Numeric data
                    try:
                        if text and text != '--' and text != 'N/A':
                            row_data.append(float(text))
                        else:
                            row_data.append(None)
                    except:
                        row_data.append(text)
            
            rows.append(row_data)
            
            # Show progress for first few rows
            if row_idx < 3:
                print(f"Row {row_idx}: {row_data[:5]}...")
        
        if not rows:
            raise Exception(f"No data rows found for {metric}")
        
        print(f"Extracted {len(rows)} rows for {metric}")
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers)
        print(f"Created DataFrame for {metric}: {df.shape}")
        print(f"Final columns: {df.columns.tolist()}")

        df = df[df['Player']!= 'Player']

        df = df.reset_index(drop=True)

        numeric_columns = ['Rk', '3PM', '3PA', '3P%', 'Ht', 'Wt']

        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=['Player'])
        
    except Exception as e:
        print(f"Scraping error for {metric}: {e}")
        import traceback
        traceback.print_exc()
        raise e

def get_playerstats_fixed(browser, season, metric):
    """
    Fixed version of kenpompy.get_playerstats that handles the column mismatch issue
    """
    try:
        # Try the normal method first
        result = kp.get_playerstats(browser, season, metric)
        return result
    except ValueError as e:
        if "Length mismatch" in str(e):
            print(f"Detected column mismatch for {metric}, trying alternative approach...")
            
            # The issue is that some stats return 9 columns but the library expects 7
            
            # Let's try getting the raw response and fix it ourselves
            try:
                import requests
                from bs4 import BeautifulSoup
                
                # Map metric to URL parameter - using correct parameters
                metric_map = {
                    "2P": "FG2Pct",
                    "3P": "FG3Pct", 
                    "FT": "FTPct"
                }
                
                if metric not in metric_map:
                    raise e
                    
                url = f"https://kenpom.com/playerstats.php?s={metric_map[metric]}"
                print(f"Trying direct URL: {url}")
                
                response = browser.get(url)
                if response.status_code != 200:
                    print(f"Failed to get page: {response.status_code}")
                    raise e
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find the actual player stats table
                tables = soup.find_all('table')
                print(f"Found {len(tables)} tables")
                
                player_table = None
                for i, table in enumerate(tables):
                    # Look for table that contains player data
                    rows = table.find_all('tr')
                    if len(rows) > 1:  # Has data beyond header
                        first_data_row = rows[1] if len(rows) > 1 else None
                        if first_data_row:
                            cells = first_data_row.find_all(['td', 'th'])
                            if len(cells) >= 4:  # Should have at least Rank, Player, Team, Stat
                                cell_texts = [cell.get_text().strip() for cell in cells]
                                # Check if this looks like player data (has names)
                                if any(len(text) > 3 and text.replace(' ', '').isalpha() for text in cell_texts[1:3]):
                                    player_table = table
                                    print(f"Found player table {i}")
                                    break
                
                if not player_table:
                    print("Could not find player table")
                    raise e
                    
                # Extract the data manually
                rows = player_table.find_all('tr')
                if len(rows) < 2:
                    print("No data rows found")
                    raise e
                    
                # Get headers
                header_row = rows[0]
                headers = [cell.get_text().strip() for cell in header_row.find_all(['th', 'td'])]
                print(f"Headers: {headers}")
                
                # Extract data
                data = []
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) == len(headers):
                        row_data = []
                        for i, cell in enumerate(cells):
                            text = cell.get_text().strip()
                            # Convert to appropriate type
                            if i == 0:  # Rank
                                try:
                                    row_data.append(int(text) if text.isdigit() else None)
                                except:
                                    row_data.append(None)
                            elif headers[i] in ['Player', 'Team', 'Yr']:
                                row_data.append(text)
                            elif headers[i] in ['Ht', 'Wt']:
                                row_data.append(text)
                            else:
                                try:
                                    row_data.append(float(text) if text and text != '--' else None)
                                except:
                                    row_data.append(text)
                        data.append(row_data)
                
                if not data:
                    print("No data extracted")
                    raise e
                    
                df = pd.DataFrame(data, columns=headers)
                print(f"Created DataFrame: {df.shape}")
                print(f"Sample data: {df.head(100)}")
                
                return [df]
                
            except Exception as scrape_error:
                print(f"Alternative approach failed: {scrape_error}")
                print("Skipping this stat for now...")
                return None
        else:
            raise e
    except KeyError as e:
        if "Metric is invalid" in str(e):
            print(f"Invalid metric name {metric}, trying workaround...")
            try:
                return handle_problematic_stat_scraping(browser, metric)
            except Exception as scrape_error:
                print(f"Workaround failed for {metric}: {scrape_error}")
                raise e
        else:
            raise e

def get_kpoy(kenpom_browser):
    kpoy_data = kp.get_kpoy(kenpom_browser)
    kpoy_df = kpoy_data[0]  # Extract DataFrame from list
    top10 = kpoy_df.head(10)
    return top10

def top_leaderboards(stat):
    return stat_leaders.get(stat)

def get_kenpom_data():
    combined_df = None
    print(f"Starting extraction. stat_leaders currently has: {len(stat_leaders)} items")

    # Process all stats (including the problematic ones)
    all_metrics = {**metrics, **problematic_stats}
    
    for stat_key, stat_name in all_metrics.items():
        try:
            print(f"Loading {stat_key} ({stat_name})...")
            
            result = get_playerstats_fixed(kenpom_browser, None, stat_name)
            
            # Handle the case where result is a list or None
            if result is None:
                print(f"Skipping {stat_key} - could not load data")
                continue
            elif isinstance(result, list):
                if len(result) > 0:
                    df = result[0]  # Take first element if it's a list
                else:
                    print(f"Empty result for {stat_key}")
                    continue
            else:
                df = result
            
            print(f"Columns for {stat_key}: {df.columns.tolist()}")
            
            # Clean up player and team names
            if "Player" in df.columns:
                df["Player"] = df["Player"].str.strip()
            if "Team" in df.columns:
                df["Team"] = df["Team"].str.strip()
            
            # Find and rename the stat column
            stat_column = None
            
            # For shooting percentages, prioritize the percentage columns
            if stat_key in ['2p', '3p', 'ft']:
                percentage_map = {
                    '2p': '2P%',
                    '3p': '3P%', 
                    'ft': 'FT%'
                }
                if percentage_map[stat_key] in df.columns:
                    stat_column = percentage_map[stat_key]
                    print(f"Found percentage column {stat_column} for {stat_key}")
            
            # If not found, try the regular logic
            if not stat_column:
                if stat_name in df.columns:
                    stat_column = stat_name
                else:
                    # Look for similar column names
                    for col in df.columns:
                        if (stat_name.lower().replace('%', '') in col.lower().replace('%', '') or
                            stat_name.lower() in col.lower()):
                            stat_column = col
                            break
            
            if stat_column:
                df = df.rename(columns={stat_column: stat_key})
                print(f"Renamed {stat_column} to {stat_key}")
            else:
                print(f"Could not find stat column for {stat_name}")
                print(f"Available columns: {df.columns.tolist()}")
                continue
            
            stat_leaders[stat_key] = df
            
            # Merge logic
            if "Player" in df.columns and "Team" in df.columns and stat_key in df.columns:
                subset = df[["Player", "Team", stat_key]]
                if combined_df is None:
                    combined_df = df.copy()
                else:
                    combined_df = pd.merge(combined_df, subset, on=["Player", "Team"], how="outer")
            else:
                print(f"Missing required columns in {stat_key}")

        except Exception as e:
            print(f"Error loading {stat_key}: {e}")
            import traceback
            traceback.print_exc()

    # Add four factors data
    try:
        four_factors_result = kp.get_fourfactors(kenpom_browser)
        
        # Handle if four_factors is also a list
        if isinstance(four_factors_result, list):
            four_factors = four_factors_result[0]
        else:
            four_factors = four_factors_result
            
        if "Team" in four_factors.columns:
            four_factors["Team"] = four_factors["Team"].str.strip()
            
        if combined_df is not None and "Team" in combined_df.columns:
            combined_df["Team"] = combined_df["Team"].str.strip()
            combined_df = pd.merge(combined_df, four_factors, on="Team", how="left")
        else:
            print("Cannot merge four factors - missing Team column")
            
    except Exception as e:
        print(f"Error merging four factors: {e}")

    print("Available stat keys:", list(stat_leaders.keys()))
    if combined_df is not None:
        print("Combined Data Preview:")
        combined_df.to_csv('full_data.csv', index=False)
        print(f"Combined DataFrame shape: {combined_df.shape}")
        
        # Show columns with actual data
        non_null_counts = combined_df.count()
        print(f"\nColumns with most data:")
        for col, count in non_null_counts.sort_values(ascending=False).head(15).items():
            print(f"  {col}: {count} players")
            
    else:
        print("No combined data created")
    
    print(f"\n=== FINAL STAT_LEADERS STATUS ===")
    print(f"stat_leaders has {len(stat_leaders)} items: {list(stat_leaders.keys())}")

    return combined_df

def get_players_with_multiple_stats(min_stats=2):
    player_stats_db = {}

    for stat_name, df in stat_leaders.items():
        if df is not None:
            print(f"Processing {stat_name}...")
        
        for index, row in df.iterrows():
            player_id = f"{row['Player']}_{row['Team']}"

            if player_id not in player_stats_db:
                player_stats_db[player_id] = {
                    'Player': row['Player'],
                    'Team': row['Team'],
                    'stat_count': 0
                }

            player_stats_db[player_id][stat_name] = row[stat_name] 
            player_stats_db[player_id]['stat_count'] += 1

    qualified_players = {}
    for player_id, player_data in player_stats_db.items():
        if player_data['stat_count'] >= min_stats:
            qualified_players[player_id] = player_data

    print(f"Found {len(qualified_players)} players with {min_stats}+ stats")
    return qualified_players

def statistical_excellence():
    """
    KenPom-Style Statistical Excellence Rating System
    
    Analyzes players who appear in KenPom's top-100 statistical categories
    and creates composite ratings based on multi-dimensional performance.
    
    SCOPE: Elite statistical performers, not necessarily overall best players
    """

    print("KENPOM-STYLE STATISTICAL EXCELLENCE RATING SYSTEM")
    print("=" * 80)
    print("WHAT THIS SYSTEM MEASURES:")
    print("   - Players excelling in multiple KenPom statistical categories")
    print("   - Multi-dimensional efficiency across offensive metrics")
    print("   - Composite ratings using KenPom's analytical philosophy")
    print("")
    print("IMPORTANT LIMITATIONS:")
    print("   • Only includes players appearing in top-100 statistical leaderboards")
    print("   • May not include all top overall players (e.g., well-rounded players")
    print("     who don't crack top-100 in individual categories)")
    print("   • Focuses on statistical excellence, not overall player rankings")
    print("=" * 80)

    # Enhanced stat weights based on KenPom philosophy
    stat_weights = {
        'ortg': 40,     # Overall offensive rating - most important if available
        'efg': 35,      # Effective FG% - shooting efficiency is crucial
        'ts': 30,       # True shooting % - another shooting metric
        'to': -30,      # Turnover rate - lower is better (negative weight)
        'arate': 25,    # Assist rate - playmaking ability
        'or': 20,       # Offensive rebounding - extra possessions
        'ftrate': 15,   # Free throw rate - getting to the line
    }

    print("\nSTATISTICAL CATEGORIES & WEIGHTS:")
    print("   (Higher weights = more important to overall rating)")
    print("-" * 60)

    for stat, weight in stat_weights.items():
        if weight > 0:
            direction = "Higher is better"
            impact = "High" if weight >= 30 else "Medium" if weight >= 20 else "Low"
        else:
            direction = "Lower is better"
            impact = "High"

        full_name = {
            'ortg': 'Offensive Rating',
            'efg': 'Effective Field Goal %',
            'ts': 'True Shooting %',
            'to': 'Turnover Rate',
            'arate': 'Assist Rate', 
            'or': 'Offensive Rebounding %',
            'ftrate': 'Free Throw Rate'
        }[stat]
        
        print(f"   {stat.upper():<8} {full_name:<25} Weight: {abs(weight):2d} ({impact:<6} impact) {direction}")

    stat_percentiles = {}
    stat_ranges = {}
    available_stats = []

    print(f"\nAVAILABLE DATA SUMMARY:")
    print("-" * 50)

    for stat_name, df in stat_leaders.items():
        if df is not None and stat_name in stat_weights:
            values = [float(x) for x in df[stat_name].tolist()]

            if stat_name == 'to':
                values.sort()
            else:
                values.sort(reverse=True)

            stat_percentiles[stat_name] = values
            stat_ranges[stat_name] = (min(values), max(values))
            available_stats.append(stat_name)

            print(f"{stat_name.upper():<8} {len(values):3d} players     Range:{min(values):5.1f} to {max(values):5.1f}")
    
    total_unique_players = len(set().union(*[
        set(df['Player'] + '_' + df['Team']) for stat, df in stat_leaders.items() 
        if df is not None and stat in stat_weights
    ]))
    
    print(f"\n   Total unique players across all categories: {total_unique_players}")
    print(f"   Available statistical categories: {len(available_stats)}")

    # Calculate composite scores
    player_scores = {}

    for stat_name, df in stat_leaders.items():
        if df is not None and stat_name in stat_weights:
            for _, row in df.iterrows():
                player_id = f"{row['Player']}_{row['Team']}"

                if player_id not in player_scores:
                    player_scores[player_id] = {
                        'Player': row['Player'],
                        'Team': row['Team'],
                        'composite_score': 0,
                        'stats_used': [],
                        'stat_details': {},
                        'tier': 'Unknown'
                    }

                #Calculating Percentile
                stat_value = float(row[stat_name])
                stat_list = stat_percentiles[stat_name]

                try:
                    if stat_name == 'to': # The lower the better for turnovers
                        percentile = (stat_list.index(stat_value) / len(stat_list)) * 100
                    else:
                        percentile = 100 - (stat_list.index(stat_value)/ len(stat_list)) * 100
                except ValueError:
                    closest_idx = min(range(len(stat_list)), key=lambda i: abs(stat_list[i] - stat_value))
                    if stat_name == 'to':
                        percentile = (closest_idx/len(stat_list)) * 100
                    else:
                        percentile = 100 - (closest_idx/len(stat_list)) * 100


                weighted_score = percentile * (abs(stat_weights[stat_name]) / 100)
                if stat_weights[stat_name] < 0:
                    weighted_score *= -1
                
                player_scores[player_id]['composite_score'] += weighted_score
                player_scores[player_id]['stats_used'].append(stat_name)
                player_scores[player_id]['stat_details'][stat_name] = {
                    'value': stat_value,
                    'percentile': percentile,
                    'weighted_score': weighted_score
                }

    print("=== DEBUGGING final_ratings creation ===")
    print(f"Available stat categories: {list(stat_leaders.keys())}")
    print(f"Player scores calculated: {len(player_scores)}")

    final_ratings = []
    print(f"final_ratings initialized: {len(final_ratings)}")

    # Your existing logic (which is correct):
    for player_id, data in player_scores.items():
        if len(data['stats_used']) >= 2:
            score = data['composite_score']
            stat_count = len(data['stats_used'])

            if score >= 60:
                data['tier'] = 'Elite Multi-Category Leader'
            elif score >= 40:
                data['tier'] = 'Excellent Multi-Category Performer'
            elif score >= 20:
                data['tier'] = 'Very Good Statistical Producer'
            elif score >= 10:
                data['tier'] = 'Above Average'

            if stat_count >= 4:
                data['diversity'] = 'Highly Diverse'
            elif stat_count >= 3:
                data['diversity'] = 'Multi-Dimensional'
            else:
                data['diversity'] = 'Specialist'

            final_ratings.append(data)

    print(f"final_ratings after processing: {len(final_ratings)} players")
    
    final_ratings.sort(key=lambda x: x['composite_score'], reverse=True)

    print(f"\nTOP 25 STATISTICAL EXCELLENCE LEADERS")
    print(" (Ranked by composite performance across multiple KenPom categories)")
    print("=" * 100)
    print(f"{'Rank':<4} {'Player':<25} {'Team':<18} {'Score':<8} {'Profile':<15} {'Key Strengths'}")
    print("-" * 110)

    for i, player in enumerate(final_ratings[:200]):
        rank = i + 1
        name = player['Player']
        team = player['Team']
        score = player['composite_score']
        diversity = player['diversity']
        stats_count = len(player['stats_used'])

        print(f"{rank:<4} {name:<25} {team:<18} {score:<6.1f} {diversity:<15}")

        sorted_stats = sorted(player['stat_details'].items(),
                              key=lambda x: abs(x[1]['weighted_score']), reverse=True)
        stat_summary = []

        for stat_name, info in sorted_stats[:3]:
            if info['percentile'] >= 95:
                emoji = "[ELITE]"
            elif info['percentile'] >= 85:
                emoji = "[EXCEL]"
            elif info['percentile'] >= 70:
                emoji = "[GOOD]"
            else:
                emoji = "[AVG]"
            stat_summary.append(f"{emoji}{stat_name.upper()}:{info['value']:.1f}")

        print(f"({stats_count} cats) {' '.join(stat_summary)}")

    print(f"\nCATEGORY LEADERS & INSIGHTS")
    print("=" * 60)

    categories = {
        'ortg': 'Highest Offensive Rating',
        'efg': 'Most Efficient Shooter (eFG%)',
        'ts': 'Best True Shooting %',
        'to': 'Best Ball Security (Lowest TO%)',
        'arate': 'Best Playmaker (Assist Rate)',
        'or': 'Best Offensive Rebounder'
    }

    for stat, description in categories.items():
        if stat in stat_percentiles and stat_percentiles[stat]:
            best_value = stat_percentiles[stat][0]
            
            # Find player with this value
            for player in final_ratings:
                if stat in player['stat_details']:
                    if abs(player['stat_details'][stat]['value'] - best_value) < 0.1:
                        print(f"{description}:")
                        print(f"   {player['Player']} ({player['Team']}) - {best_value:.1f}")
                        print(f"   Overall Rating Rank: #{final_ratings.index(player) + 1}")
                        break
            print()

    # Summary and Insights
    print(f"RATING SYSTEM SUMMARY")
    print("-" * 40)
    qualified_players = len(final_ratings) + 1
    avg_score = sum(p['composite_score'] for p in final_ratings) / qualified_players
    
    tier_counts = {}
    diversity_counts = {}
    for player in final_ratings:
        tier = player['tier']
        diversity = player['diversity']
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
        diversity_counts[diversity] = diversity_counts.get(diversity, 0) + 1
    
    print(f"Players meeting criteria (2+ categories): {qualified_players}")
    print(f"Average composite score: {avg_score:.1f}")
    if len(final_ratings) > 0:
        print(f"Score range: {final_ratings[-1]['composite_score']:.1f} to {final_ratings[0]['composite_score']:.1f}")
    else:
        print("No players qualified for final ratings")
    
    print(f"\nPlayer Diversity Profiles:")
    for diversity, count in sorted(diversity_counts.items(), reverse=True):
        percentage = (count / qualified_players) * 100
        print(f"   {diversity:<20} {count:3d} players ({percentage:4.1f}%)")
    
    print(f"\nWHAT THESE RANKINGS TELL US:")
    print("   • Top players excel in multiple statistical categories")
    print("   • Elite performers combine efficiency with production")  
    print("   • Multi-dimensional players score higher than one-category specialists")
    print("   • Rankings reflect KenPom's emphasis on efficiency metrics")
    
    print(f"\nFOR FURTHER ANALYSIS:")
    print("   • Compare these statistical leaders with team performance")
    print("   • Look for players strong in complementary categories")
    print("   • Consider context of competition level and team system")
    print("   • Use as starting point for deeper player evaluation")
    
    return final_ratings

if __name__ == "__main__":
    # Load KenPom data
    print("Loading KenPom statistical data...")
    result = get_kenpom_data()
    
    # Run statistical excellence rating system
    print("\nRunning Statistical Excellence Analysis...")
    kenpom_ratings = statistical_excellence()
    
    # Optional: Show players with multiple stats
    print("\nFinding multi-dimensional players...")
    multi_stat_players = get_players_with_multiple_stats(min_stats=3)
    
    print(f"\nAnalysis complete! Found {len(kenpom_ratings)} rated players.")