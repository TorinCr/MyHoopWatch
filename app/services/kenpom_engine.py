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
        
        # Show a sample of the data
        if len(df) > 0:
            print("Sample data:")
            print(df.head(2))
        
        return [df]  # Return as list to match kenpompy format
        
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
                print(f"Sample data: {df.head(2)}")
                
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

def kenpom_ratings():
    combined_df = None

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
        print(combined_df.head())
        print(f"Combined DataFrame shape: {combined_df.shape}")
        
        # Show columns with actual data
        non_null_counts = combined_df.count()
        print(f"\nColumns with most data:")
        for col, count in non_null_counts.sort_values(ascending=False).head(15).items():
            print(f"  {col}: {count} players")
            
    else:
        print("No combined data created")

    return combined_df

def get_stat_leaders(stat_key, n=10):
    """Get top N players for a specific stat"""
    if stat_key not in stat_leaders:
        print(f"Stat {stat_key} not available. Available stats: {list(stat_leaders.keys())}")
        return None
    
    df = stat_leaders[stat_key]
    # Sort by rank if available, otherwise by the stat value
    if 'Rank' in df.columns:
        return df.head(n)
    elif stat_key in df.columns:
        return df.sort_values(stat_key, ascending=False).head(n)
    else:
        return df.head(n)

# Run the main function
if __name__ == "__main__":
    result = kenpom_ratings()