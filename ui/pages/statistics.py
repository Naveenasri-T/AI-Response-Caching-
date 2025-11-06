"""
Statistics Page
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

def show():
    """Display statistics and analytics"""
    
    st.header("📊 System Statistics & Analytics")
    
    # Fetch statistics
    try:
        response = requests.get(f"{API_BASE_URL}/statistics", timeout=10)
        
        if response.status_code == 200:
            stats = response.json()
            
            # Overview metrics
            st.subheader("📈 Performance Overview")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_requests = stats.get("total_requests", 0)
                st.metric("Total Requests", f"{total_requests:,}", help="Total API requests processed")
            
            with col2:
                cache_hits = stats.get("cache_hits", 0)
                st.metric("Cache Hits", f"{cache_hits:,}", delta="✅ Cached", help="Requests served from cache")
            
            with col3:
                cache_misses = stats.get("cache_misses", 0)
                st.metric("Cache Misses", f"{cache_misses:,}", delta="🤖 AI Model", help="Requests that used AI model")
            
            with col4:
                hit_rate = stats.get("cache_hit_rate", 0)
                delta_color = "normal" if hit_rate > 50 else "inverse"
                st.metric("Hit Rate", f"{hit_rate:.1f}%", 
                         delta=f"{hit_rate:.1f}%",
                         delta_color=delta_color,
                         help="Percentage of requests served from cache")
            
            st.markdown("---")
            
            # Charts Row 1
            col1, col2 = st.columns(2)
            
            with col1:
                # Cache Performance Pie Chart
                st.subheader("🎯 Cache Performance")
                
                if cache_hits + cache_misses > 0:
                    fig = go.Figure(data=[go.Pie(
                        labels=['✅ Cache Hits (Fast!)', '🤖 Cache Misses (Slow)'],
                        values=[cache_hits, cache_misses],
                        marker_colors=['#2ecc71', '#e74c3c'],
                        hole=0.4,
                        textinfo='label+percent+value',
                        textfont_size=14
                    )])
                    fig.update_layout(
                        showlegend=True,
                        height=350,
                        margin=dict(t=20, b=20, l=20, r=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Performance insight
                    if hit_rate > 70:
                        st.success(f"🎉 Excellent! {hit_rate:.1f}% cache hit rate means **{int((1200/12)*hit_rate/100)}× faster** on average!")
                    elif hit_rate > 40:
                        st.info(f"👍 Good! {hit_rate:.1f}% cache hit rate. More repeated requests will improve this.")
                    else:
                        st.warning(f"⚠️ {hit_rate:.1f}% cache hit rate. Try making repeated requests to see caching benefits!")
                else:
                    st.info("No data yet. Make some requests to see statistics!")
            
            with col2:
                # Cache Source Distribution
                st.subheader("💾 Cache Source Distribution")
                
                cache_sources = stats.get("cache_sources", {})
                if cache_sources:
                    # Create bar chart with colors
                    sources = list(cache_sources.keys())
                    values = list(cache_sources.values())
                    colors = ['#667eea' if s == 'memcache' else '#764ba2' if s == 'redis' else '#f093fb' 
                             for s in sources]
                    
                    fig = go.Figure(data=[go.Bar(
                        x=[s.upper() for s in sources],
                        y=values,
                        marker_color=colors,
                        text=values,
                        textposition='auto',
                    )])
                    fig.update_layout(
                        showlegend=False,
                        height=350,
                        xaxis_title="Source",
                        yaxis_title="Requests",
                        margin=dict(t=20, b=20, l=20, r=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show breakdown
                    memcache_pct = (cache_sources.get('memcache', 0) / total_requests * 100) if total_requests > 0 else 0
                    redis_pct = (cache_sources.get('redis', 0) / total_requests * 100) if total_requests > 0 else 0
                    model_pct = (cache_sources.get('model', 0) / total_requests * 100) if total_requests > 0 else 0
                    
                    st.caption(f"⚡ **Memcached (L1)**: {memcache_pct:.1f}% (~2ms each)")
                    st.caption(f"💾 **Redis (L2)**: {redis_pct:.1f}% (~12ms each)")
                    st.caption(f"🤖 **AI Model**: {model_pct:.1f}% (~1200ms each)")
                else:
                    st.info("No cache source data available yet")
            
            st.markdown("---")
            
            # Response time comparison
            st.subheader("⏱️ Response Time Comparison")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                    <h4>⚡ Memcached (L1)</h4>
                    <h2>~2ms</h2>
                    <p>Ultra-fast in-memory</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                    <h4>💾 Redis (L2)</h4>
                    <h2>~12ms</h2>
                    <p>Fast persistent cache</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                    <h4>🤖 Model (Cold)</h4>
                    <h2>~1200ms</h2>
                    <p>AI model processing</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Performance gain
            st.markdown("---")
            st.subheader("🚀 Performance Gain")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.success("**Memcached vs Model**: 600× faster ⚡")
                st.success("**Redis vs Model**: 100× faster 🚀")
            
            with col2:
                st.info("**Average Speedup**: 250-600× with cache hits!")
                st.info("**API Cost Savings**: Only pay for cache misses!")
            
            # Task type distribution
            st.markdown("---")
            st.subheader("📋 Task Distribution")
            
            task_types = stats.get("task_types", {})
            if task_types:
                df = pd.DataFrame(list(task_types.items()), columns=['Task', 'Count'])
                df = df.sort_values('Count', ascending=True)
                
                fig = px.bar(df, x='Count', y='Task', orientation='h',
                           color='Count', color_continuous_scale='Viridis')
                fig.update_layout(
                    showlegend=False,
                    height=300,
                    margin=dict(t=0, b=0, l=0, r=0)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No task data available yet")
            
            # Recent activity with caching history
            st.markdown("---")
            st.subheader("🕐 Recent Activity & Caching History")
            
            recent_requests = stats.get("recent_requests", [])
            if recent_requests:
                # Create DataFrame
                df = pd.DataFrame(recent_requests)
                
                # Add visual indicators
                if 'cache_source' in df.columns:
                    df['Cache Status'] = df['cache_source'].apply(
                        lambda x: '⚡ Memcached' if x == 'memcache' 
                        else '💾 Redis' if x == 'redis' 
                        else '🤖 AI Model'
                    )
                
                # Display as table
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "timestamp": st.column_config.DatetimeColumn(
                            "Time",
                            format="MMM DD, HH:mm:ss"
                        ),
                        "cache_source": st.column_config.TextColumn(
                            "Source",
                        ),
                        "response_time_ms": st.column_config.NumberColumn(
                            "Response (ms)",
                            format="%.2f"
                        )
                    }
                )
                
                # Show caching trend
                if len(recent_requests) > 5:
                    st.markdown("### 📈 Caching Trend (Last Requests)")
                    
                    # Create timeline chart
                    df['Request #'] = range(len(df), 0, -1)
                    
                    fig = go.Figure()
                    
                    # Add line for response time
                    fig.add_trace(go.Scatter(
                        x=df['Request #'],
                        y=df['response_time_ms'],
                        mode='lines+markers',
                        name='Response Time',
                        line=dict(color='#667eea', width=3),
                        marker=dict(
                            size=10,
                            color=df['cache_source'].map({
                                'memcache': '#2ecc71',
                                'redis': '#f39c12',
                                'model': '#e74c3c'
                            }),
                            line=dict(width=2, color='white')
                        ),
                        text=df['Cache Status'],
                        hovertemplate='<b>%{text}</b><br>Response: %{y:.2f}ms<extra></extra>'
                    ))
                    
                    fig.update_layout(
                        height=300,
                        xaxis_title="Request Number (Most Recent →)",
                        yaxis_title="Response Time (ms)",
                        showlegend=False,
                        margin=dict(t=20, b=20, l=20, r=20),
                        yaxis_type="log"  # Log scale to show differences better
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.caption("🟢 Green = Memcached (2ms) | 🟠 Orange = Redis (12ms) | 🔴 Red = AI Model (1200ms)")
            else:
                st.info("No recent activity. Start making requests to see history!")
        
        else:
            st.error(f"Failed to fetch statistics: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        st.warning("⚠️ Make sure the FastAPI server is running")
