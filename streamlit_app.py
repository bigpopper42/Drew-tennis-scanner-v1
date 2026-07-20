import json
from typing import List
import pandas as pd
import streamlit as st
from scanner.models import MatchInput
from scanner.decision import evaluate_match
from scanner.database import init_db, save_recommendation, load_recommendations, update_result
from scanner.api_tennis import get_live_events
from scanner.polymarket import search_markets_locally

st.set_page_config(page_title='Tennis Scanner Assistant', page_icon='🎾', layout='wide')
init_db()
st.title('🎾 Tennis Scanner Assistant')
st.caption('Version 1–2: scanner, decision engine, position sizing, and paper log. It does not place real trades.')

tab1, tab2, tab3, tab4 = st.tabs(['Scan a match','Trade log','Live tennis feed (beta)','Polymarket market search'])
with tab1:
    st.subheader('Enter the live match information')
    st.info('Copy the live numbers from your tennis app. This app applies the hard rules and Stability Score automatically.')
    with st.form('scan_form'):
        c1,c2,c3=st.columns(3)
        with c1:
            player=st.text_input('Player being backed','Example Player'); opponent=st.text_input('Opponent','Example Opponent'); tournament=st.text_input('Tournament','ATP Event')
            tournament_level=st.selectbox('Tournament level',['Grand Slam','Masters 1000','ATP 500','ATP 250','Challenger','Lower'])
            surface=st.selectbox('Surface',['Hard','Clay','Grass','Indoor']); ranking=st.number_input('Official ranking (0 if unknown)',min_value=0,value=25)
        with c2:
            bankroll=st.number_input('Current bankroll ($)',min_value=0.0,value=100.0,step=1.0); market_price=st.number_input('Polymarket YES price (cents)',min_value=1.0,max_value=99.9,value=98.0,step=.1)
            match_closing_set=st.checkbox('Winning this set wins the match',value=True); break_lead=st.number_input('Break lead',min_value=0,max_value=5,value=1)
            serving=st.checkbox('Backed player is serving',value=True); tiebreak=st.checkbox('Current set is a tiebreak',value=False)
            games_in_set=st.number_input('Backed player games won in current set',min_value=0,max_value=7,value=5)
            current_game_score=st.selectbox('Current game score (backed player first)',['0-0','15-0','30-0','40-0','0-15','15-15','30-15','40-15','0-30','15-30','30-30','40-30','0-40','15-40','30-40','Deuce','Ad-In','Ad-Out'])
        with c3:
            completed_sets=st.number_input('Completed sets',min_value=0,max_value=4,value=1); breaks_by_set_text=st.text_input('Breaks suffered in completed sets (comma separated)','1')
            service_points=st.number_input('Service points won %',0.0,100.0,67.0,.1); first_serve_points=st.number_input('First-serve points won %',0.0,100.0,75.0,.1)
            first_serve_in=st.number_input('First serves in %',0.0,100.0,63.0,.1); breaks_total=st.number_input('Total breaks suffered',0,20,1)
            break_points_faced=st.number_input('Break points faced',0,50,3); comfortable_holds=st.number_input('Comfortable holds %',0.0,100.0,65.0,.1)
            df_rate=st.number_input('Double faults per service game',0.0,5.0,.10,.01)
        c4,c5,c6=st.columns(3)
        with c4: recent_form=st.selectbox('Recent form + opponent quality',['Excellent','Strong','Good','Mixed','Weak','Very poor'],index=1)
        with c5: surface_form=st.selectbox('Recent surface evidence',['Strong','Neutral','Weak'],index=1)
        with c6: notes=st.text_area('Notes','')
        submitted=st.form_submit_button('Analyze match',type='primary',use_container_width=True)
    if submitted:
        try: breaks_by_set=[int(x.strip()) for x in breaks_by_set_text.split(',') if x.strip()]
        except ValueError: st.error('Use numbers separated by commas, such as 1,2.'); st.stop()
        match=MatchInput(player,opponent,tournament,tournament_level,surface,market_price,bankroll,match_closing_set,int(break_lead),serving,tiebreak,int(games_in_set),current_game_score,int(completed_sets),breaks_by_set,service_points,first_serve_points,first_serve_in,int(breaks_total),int(break_points_faced),comfortable_holds,df_rate,recent_form,int(ranking) if ranking else None,surface_form,notes)
        d=evaluate_match(match)
        (st.success if d.status=='TRADE' else st.warning if d.status=='WAIT' else st.error)(d.status)
        a,b,c=st.columns(3); a.metric('Stability Score',f'{d.score:.1f}/100' if d.score else 'Not scored'); b.metric('Required Score',f'{d.minimum_score:.1f}' if d.minimum_score else 'Hard rules first'); c.metric('Suggested stake',f'${d.stake_amount:.2f} ({d.stake_pct*100:.0f}%)')
        st.write(d.reason); left,right=st.columns(2)
        with left:
            st.markdown('#### Passed')
            for x in d.passed: st.write('✅',x)
        with right:
            st.markdown('#### Risks / blockers')
            for x in d.concerns: st.write('⚠️',x)
        if d.score_parts:
            sdf=pd.DataFrame([{'Factor':k,'Points':v} for k,v in d.score_parts.items()]).sort_values('Points',ascending=False)
            st.markdown('#### Score breakdown'); st.dataframe(sdf,use_container_width=True,hide_index=True)
        record={'player':player,'opponent':opponent,'tournament':tournament,'market_price_cents':market_price,'status':d.status,'stability_score':d.score,'required_score':d.minimum_score,'stake_pct':d.stake_pct,'stake_amount':d.stake_amount,'bankroll':bankroll,'notes':notes}
        if st.button('Save this recommendation to paper log'): save_recommendation(record); st.success('Saved.')
with tab2:
    st.subheader('Paper-trading log'); df=load_recommendations()
    if df.empty: st.info('No recommendations saved yet.')
    else:
        st.dataframe(df,use_container_width=True,hide_index=True); st.download_button('Download log as CSV',df.to_csv(index=False).encode(),'tennis_scanner_log.csv','text/csv')
        st.markdown('#### Update a result'); c1,c2,c3=st.columns(3)
        with c1: row_id=st.number_input('Log row ID',min_value=1,step=1)
        with c2: result=st.selectbox('Result',['WIN','LOSS','VOID','OPEN'])
        with c3: pnl=st.number_input('Profit / loss ($)',value=0.0,step=.01)
        if st.button('Update result'): update_result(int(row_id),result,pnl); st.success('Updated. Refresh the page.')
with tab3:
    st.subheader("Live tennis feed (beta)")
    st.warning("This fetches raw live events. Automatic field mapping is the next integration step.")

    try:
        default_key = st.secrets.get("API_TENNIS_KEY", "")
    except Exception:
        default_key = ""

    api_key = st.text_input(
        "API Tennis key",
        value=default_key,
        type="password"
    )

    if st.button("Fetch live tennis events"):
        try:
            events = get_live_events(api_key)
            st.success(f"Fetched {len(events)} live event(s).")

            if events:
                st.success(f"Found {len(events)} live match(es).")

                for i, match in enumerate(events):
                    player1 = match.get("event_first_player", "Unknown")
                    player2 = match.get("event_second_player", "Unknown")
                    score = match.get("event_final_result", "Live")
                    tournament = match.get("tournament_name", "")

                    with st.container():
                        st.markdown(f"### {player1} vs {player2}")
                        st.write(f"**Tournament:** {tournament}")
                        st.write(f"**Score:** {score}")

                        if st.button("Analyze", key=f"analyze_{i}"):
                            st.info("Analysis coming in the next update.")

                        st.divider()

            else:
                st.info("No live events returned.")

        except Exception as e:
            st.error(f"Could not fetch live events: {e}")
with tab4:
    st.subheader('Polymarket public market search'); st.caption('Read-only. No wallet or private key is used.')
    query=st.text_input('Search active markets','tennis')
    if st.button('Search Polymarket'):
        try:
            markets=search_markets_locally(query); st.success(f'Found {len(markets)} matching market(s).')
            if markets:
                rows=[{'question':m.get('question'),'slug':m.get('slug'),'outcomes':m.get('outcomes'),'outcomePrices':m.get('outcomePrices'),'volume':m.get('volume'),'liquidity':m.get('liquidity')} for m in markets]
                st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
            else: st.info('No matching markets found in the current batch.')
        except Exception as e: st.error(f'Could not fetch Polymarket markets: {e}')
st.divider(); st.caption('Experimental tool. Keep it in paper-trading/manual-confirmation mode until tested on a large sample.')
