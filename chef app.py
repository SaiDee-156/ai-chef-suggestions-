# ============================================================
# ITALIAN FOOD MENU ANALYZER - CHEF RECOMMENDATION SYSTEM
# WITH BUFFET-SPECIFIC QUANTITY AND FUTURE SUGGESTIONS
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px

# ============================================================
# STREAMLIT CONFIG
# ============================================================
st.set_page_config(
    page_title="Italian Food Chef Advisor",
    page_icon="🍝",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🇮🇹 Italian Food Chef Recommendation System")
st.markdown("### AI-Powered Future Cooking Suggestions for Chef")
st.markdown("---")

# ============================================================
# DATA LOADING & PROCESSING
# ============================================================
@st.cache_data
def load_data():
    """Load and preprocess the Italian food data"""
    try:
        # Try to load from pickle first
        df = pd.read_pickle("italian_food_clean.pkl")
    except:
        # Create sample data if file not found
        sample_data = {
            "ID": list(range(1, 31)),
            "Item Name": [
                "Bruschetta Classica", "Arancini al Ragù", "Caprese Salad", "Calamari Fritti", "Vitello Tonnato",
                "Panzanella", "Prosciutto e Melone", "Focaccia", "Olive Ascolane", "Carciofi alla Giudia",
                "Spaghetti Carbonara", "Lasagna", "Penne all'Arrabbiata", "Risotto ai Funghi", "Gnocchi al Pesto",
                "Pizza Margherita", "Pizza Quattro Formaggi", "Calzone", "Focaccia di Recco", "Pizza al Taglio",
                "Tiramisu", "Panna Cotta", "Cannoli", "Zabaglione", "Semifreddo",
                "Torta della Nonna", "Crostata di Ricotta", "Biscotti", "Amaretti", "Cantucci"
            ],
            "Category": ["Starter"]*10 + ["Pasta"]*5 + ["Pizza"]*5 + ["Dessert"]*5 + ["Cake"]*5,
            "Type": ["Veg", "Non-Veg", "Veg", "Non-Veg", "Non-Veg"]*6,
            "Buffet Status": ["Present"]*25 + ["Absent"]*5,
            "Origin/Details": ["Traditional Italian"]*30
        }
        df = pd.DataFrame(sample_data)
    
    return df

df = load_data()

# ============================================================
# SIDEBAR - FILTERS
# ============================================================
st.sidebar.header("🍽️ Menu Filters")

# Category filter
categories = sorted(df["Category"].unique())
selected_categories = st.sidebar.multiselect(
    "Select Categories",
    categories,
    default=categories[:3] if len(categories) > 3 else categories
)

# Type filter
food_types = sorted(df["Type"].unique())
selected_types = st.sidebar.multiselect(
    "Select Food Type",
    food_types,
    default=food_types
)

# Buffet status filter
buffet_options = sorted(df["Buffet Status"].unique())
selected_buffet = st.sidebar.multiselect(
    "Buffet Status",
    buffet_options,
    default=buffet_options
)

# Filter data
filtered_df = df[
    (df["Category"].isin(selected_categories if selected_categories else categories)) &
    (df["Type"].isin(selected_types if selected_types else food_types)) &
    (df["Buffet Status"].isin(selected_buffet if selected_buffet else buffet_options))
]

# ============================================================
# FUTURE SUGGESTION FUNCTIONS
# ============================================================

def generate_future_suggestions(df, event_type="Normal Day", guests=100, season="Summer"):
    """
    Generate specific future cooking suggestions for the chef
    """
    suggestions = []
    
    # Get buffet items
    buffet_items = df[df["Buffet Status"] == "Present"]
    
    if len(buffet_items) == 0:
        return [{
            "type": "warning",
            "title": "⚠️ No Buffet Items Selected",
            "message": "No buffet items found in current selection",
            "details": ["Please adjust filters to include buffet items"],
            "action_items": ["Select 'Present' in Buffet Status filter"]
        }]
    
    # Analyze category distribution
    category_counts = df["Category"].value_counts()
    most_common_category = category_counts.idxmax() if len(category_counts) > 0 else "None"
    
    # SUGGESTION 1: Based on event type
    event_suggestions = {
        "Wedding": {
            "extra_items": 8,
            "focus_categories": ["Cake", "Pastry", "Dessert", "Fried", "Seafood"],
            "message": "Weddings require elegant presentation and variety",
            "specific_suggestions": [
                "Prepare 50% extra desserts for wedding guests",
                "Focus on visually appealing items like Caprese Salad",
                "Include both hot and cold canapés"
            ]
        },
        "Corporate Event": {
            "extra_items": 5,
            "focus_categories": ["Fried", "Starter", "Salad", "Cold Meat"],
            "message": "Corporate events need quick, easy-to-eat finger foods",
            "specific_suggestions": [
                "Prepare 30% extra fried items (they disappear quickly)",
                "Focus on bite-sized portions",
                "Include vegetarian options for diverse preferences"
            ]
        },
        "Birthday Party": {
            "extra_items": 6,
            "focus_categories": ["Cake", "Pastry", "Fried", "Pasta"],
            "message": "Birthday parties need fun, crowd-pleasing foods",
            "specific_suggestions": [
                "Prepare 40% extra cakes and desserts",
                "Include kid-friendly fried items",
                "Make pasta dishes in bulk (they're always popular)"
            ]
        },
        "Festival": {
            "extra_items": 10,
            "focus_categories": ["Fried", "Street Food", "Dessert"],
            "message": "Festivals require high-volume, portable foods",
            "specific_suggestions": [
                "Prepare 60% extra of everything (crowds are unpredictable)",
                "Focus on foods that can be eaten while standing",
                "Have backup ingredients ready for popular items"
            ]
        },
        "Normal Day": {
            "extra_items": 3,
            "focus_categories": ["Salad", "Pasta", "Main Course"],
            "message": "Regular service needs balanced options",
            "specific_suggestions": [
                "Prepare 20% extra of daily specials",
                "Monitor sales and adjust quantities tomorrow",
                "Focus on seasonal ingredients"
            ]
        }
    }
    
    event_info = event_suggestions.get(event_type, event_suggestions["Normal Day"])
    
    # Add event-based suggestions
    suggestions.append({
        "type": "event",
        "title": f"🎉 {event_type} Preparation",
        "message": event_info["message"],
        "details": event_info["specific_suggestions"],
        "action_items": [
            f"Cook {event_info['extra_items']} extra items",
            f"Focus on {', '.join(event_info['focus_categories'][:3])}",
            f"Prepare for {guests} guests"
        ]
    })
    
    # SUGGESTION 2: Based on season
    seasonal_advice = {
        "Summer": {
            "increase": ["Salad", "Seafood", "Cold Meat", "Dessert"],
            "decrease": ["Fried", "Heavy Pasta"],
            "tips": [
                "People eat lighter in summer",
                "Cold dishes are more popular",
                "Focus on fresh, crisp ingredients"
            ]
        },
        "Winter": {
            "increase": ["Fried", "Pasta", "Cake", "Main Course"],
            "decrease": ["Salad", "Cold Meat"],
            "tips": [
                "Comfort foods are key in winter",
                "Hot, hearty dishes sell well",
                "Rich desserts are popular"
            ]
        },
        "Spring": {
            "increase": ["Starter", "Salad", "Seafood"],
            "decrease": ["Heavy Main Courses"],
            "tips": [
                "Light, fresh flavors work well",
                "Seasonal vegetables are a hit",
                "Balance between light and hearty"
            ]
        },
        "Autumn": {
            "increase": ["Pasta", "Cake", "Fried"],
            "decrease": ["Summer Salads"],
            "tips": [
                "Harvest flavors are popular",
                "Warming foods start to sell",
                "Transition to heartier menu"
            ]
        }
    }
    
    season_info = seasonal_advice.get(season, seasonal_advice["Summer"])
    
    # Check if we have items in these categories
    increase_items = []
    for category in season_info["increase"]:
        if category in df["Category"].values:
            items_in_category = df[df["Category"] == category]["Item Name"].tolist()
            increase_items.extend(items_in_category[:2])
    
    if increase_items:
        suggestions.append({
            "type": "seasonal",
            "title": f"🌤️ {season} Season Strategy",
            "message": f"In {season}, people prefer different types of food",
            "details": season_info["tips"],
            "action_items": [
                f"Cook more: {', '.join(increase_items[:3])}",
                f"Focus on: {', '.join(season_info['increase'][:3])}",
                f"Reduce emphasis on: {', '.join(season_info['decrease'][:3])}"
            ]
        })
    
    # SUGGESTION 3: Specific items to cook extra
    # Based on category popularity and prep time
    quick_items = []
    bulk_items = []
    
    for _, item in buffet_items.iterrows():
        if item["Category"] in ["Fried", "Pasta"]:
            quick_items.append(item["Item Name"])
        elif item["Category"] in ["Cake", "Pastry", "Cookie"]:
            bulk_items.append(item["Item Name"])
    
    if quick_items:
        suggestions.append({
            "type": "specific",
            "title": "⚡ Quick-to-Prep Items",
            "message": "These items can be made quickly if you run out",
            "details": [
                "Keep ingredients ready",
                "Can be made in batches",
                "Popular with last-minute orders"
            ],
            "action_items": [
                f"Have ingredients ready for: {', '.join(quick_items[:3])}",
                "Prep stations in advance",
                "Train staff on quick preparation"
            ]
        })
    
    if bulk_items:
        suggestions.append({
            "type": "specific",
            "title": "📦 Make-in-Advance Items",
            "message": "Prepare these in bulk before service",
            "details": [
                "Better quality when made in advance",
                "Saves time during service",
                "Consistent results"
            ],
            "action_items": [
                f"Bake extra: {', '.join(bulk_items[:3])}",
                "Store properly",
                "Portion before service"
            ]
        })
    
    return suggestions

def generate_daily_plan(df, day_of_week, expected_customers):
    """
    Generate daily cooking plan based on day of week
    """
    day_plans = {
        "Monday": {
            "focus": "Comfort foods",
            "extra_prep": 0.8,
            "popular_items": ["Pasta", "Soup", "Salad"],
            "notes": "Slow start to the week"
        },
        "Tuesday": {
            "focus": "Regular menu",
            "extra_prep": 0.9,
            "popular_items": ["Fried", "Main Course"],
            "notes": "Steady business"
        },
        "Wednesday": {
            "focus": "Mid-week specials",
            "extra_prep": 1.0,
            "popular_items": ["Pasta", "Seafood", "Dessert"],
            "notes": "Try new items"
        },
        "Thursday": {
            "focus": "Weekend prep",
            "extra_prep": 1.1,
            "popular_items": ["Fried", "Appetizers"],
            "notes": "Start weekend preparation"
        },
        "Friday": {
            "focus": "Weekend crowd",
            "extra_prep": 1.3,
            "popular_items": ["Seafood", "Fried", "Dessert"],
            "notes": "Busy night - prepare extra"
        },
        "Saturday": {
            "focus": "Special occasions",
            "extra_prep": 1.5,
            "popular_items": ["Cake", "Pastry", "Specialty Items"],
            "notes": "Maximum preparation needed"
        },
        "Sunday": {
            "focus": "Family meals",
            "extra_prep": 1.2,
            "popular_items": ["Pasta", "Main Course", "Dessert"],
            "notes": "Family dining focus"
        }
    }
    
    plan = day_plans.get(day_of_week, day_plans["Monday"])
    
    # Find specific items to focus on
    focus_items = []
    for category in plan["popular_items"]:
        category_items = df[df["Category"] == category]
        if len(category_items) > 0:
            focus_items.extend(category_items["Item Name"].head(2).tolist())
    
    return {
        "day": day_of_week,
        "focus": plan["focus"],
        "focus_items": focus_items[:3],
        "notes": plan["notes"],
        "expected_customers": expected_customers,
        "extra_percentage": int((plan["extra_prep"] - 1) * 100)
    }

# ============================================================
# MAIN DASHBOARD
# ============================================================

# Display filtered data info
st.subheader("📊 Current Menu Selection")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Items", len(filtered_df))

with col2:
    buffet_count = len(filtered_df[filtered_df["Buffet Status"] == "Present"])
    st.metric("Buffet Items", buffet_count)

with col3:
    veg_count = len(filtered_df[filtered_df["Type"] == "Veg"])
    st.metric("Vegetarian Items", veg_count)

# ============================================================
# FUTURE SUGGESTIONS INTERFACE
# ============================================================
st.markdown("---")
st.subheader("🔮 FUTURE COOKING SUGGESTIONS FOR CHEF")

# Create tabs for different suggestion types
future_tab1, future_tab2, future_tab3, future_tab4, future_tab5 = st.tabs([
    "📅 Daily Plan", 
    "🎯 Event Prep", 
    "🌤️ Seasonal", 
    "⚡ Quick Actions", 
    "📈 Long-term"
])

with future_tab1:
    st.subheader("📅 Daily Cooking Plan")
    
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        selected_day = st.selectbox(
            "Select Day",
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            index=datetime.now().weekday()
        )
    
    with col_d2:
        daily_customers = st.number_input(
            "Expected Customers",
            min_value=20,
            max_value=500,
            value=120,
            step=10
        )
    
    if st.button("📋 Generate Daily Plan", key="daily_plan"):
        daily_plan = generate_daily_plan(filtered_df, selected_day, daily_customers)
        
        # Display plan
        st.success(f"✅ {selected_day} Cooking Plan")
        
        col_plan1, col_plan2, col_plan3 = st.columns(3)
        
        with col_plan1:
            st.metric("Extra % Needed", f"{daily_plan['extra_percentage']}%")
        
        with col_plan2:
            st.metric("Expected Customers", daily_plan["expected_customers"])
        
        with col_plan3:
            st.metric("Focus", daily_plan["focus"])
        
        # Focus items
        st.markdown("### 🎯 Focus on These Items:")
        for item in daily_plan["focus_items"]:
            st.markdown(f"• **{item}**")
        
        # Daily notes
        st.markdown("### 📝 Daily Notes:")
        st.info(daily_plan["notes"])
        
        # Hourly breakdown
        st.markdown("### 🕒 Hourly Breakdown:")
        
        hourly_schedule = {
            "Morning Prep (8 AM - 11 AM)": [
                "Check inventory",
                "Prep vegetables",
                "Make sauces",
                "Prepare doughs"
            ],
            "Lunch Rush (11 AM - 2 PM)": [
                "Cook pasta",
                "Fry items",
                "Plate salads",
                "Monitor buffet"
            ],
            "Afternoon (2 PM - 5 PM)": [
                "Clean and reset",
                "Prep for dinner",
                "Make desserts",
                "Restock"
            ],
            "Dinner Service (5 PM - 10 PM)": [
                "Full service",
                "Extra staff",
                "Quick replenishment",
                "Quality check"
            ]
        }
        
        for time_slot, tasks in hourly_schedule.items():
            with st.expander(f"⏰ {time_slot}"):
                for task in tasks:
                    st.checkbox(task)

with future_tab2:
    st.subheader("🎯 Event-Specific Preparation")
    
    col_e1, col_e2 = st.columns(2)
    
    with col_e1:
        event_type = st.selectbox(
            "Event Type",
            ["Wedding", "Corporate Event", "Birthday Party", "Festival", "Conference", "Normal Day"]
        )
    
    with col_e2:
        event_guests = st.number_input(
            "Number of Guests",
            min_value=20,
            max_value=1000,
            value=150,
            step=10
        )
    
    if st.button("🎪 Generate Event Plan", key="event_plan"):
        suggestions = generate_future_suggestions(
            filtered_df, 
            event_type, 
            event_guests,
            "Summer"
        )
        
        # Display suggestions
        for suggestion in suggestions:
            if suggestion["type"] == "event":
                st.markdown(f"""
                <div style='background-color: #E3F2FD; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                    <h4 style='color: #1976D2;'>🎉 {suggestion['title']}</h4>
                    <p><strong>{suggestion['message']}</strong></p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### 📋 Specific Suggestions:")
                for detail in suggestion["details"]:
                    st.markdown(f"• {detail}")
                
                st.markdown("#### 🎯 Action Items:")
                for action in suggestion["action_items"]:
                    st.markdown(f"✅ {action}")
        
        # Event-specific quantities guide
        st.markdown("### 📊 Event Quantities Guide:")
        
        event_quantities = {
            "Wedding": {
                "per_25_guests": 1.5,
                "focus": "Quality over quantity",
                "timing": "3-hour service"
            },
            "Corporate Event": {
                "per_25_guests": 1.2,
                "focus": "Efficiency and variety",
                "timing": "2-hour reception"
            },
            "Birthday Party": {
                "per_25_guests": 1.3,
                "focus": "Fun and variety",
                "timing": "3-hour party"
            },
            "Festival": {
                "per_25_guests": 1.6,
                "focus": "High volume, quick service",
                "timing": "All day"
            }
        }
        
        event_info = event_quantities.get(event_type, {"per_25_guests": 1.1, "focus": "Standard", "timing": "2 hours"})
        
        # Calculate batches
        batches_needed = int((event_guests / 25) * event_info["per_25_guests"])
        
        st.info(f"""
        **📈 For {event_guests} guests at a {event_type}:**
        - Prepare **{batches_needed} batches** of each popular item
        - Focus on: **{event_info['focus']}**
        - Service timing: **{event_info['timing']}**
        - Have **backup ingredients** for 20% more guests
        """)

with future_tab3:
    st.subheader("🌤️ Seasonal Strategy")
    
    col_s1, col_s2 = st.columns(2)
    
    with col_s1:
        selected_season = st.selectbox(
            "Current Season",
            ["Summer", "Winter", "Spring", "Autumn"],
            index=0
        )
    
    with col_s2:
        season_duration = st.slider(
            "Season Duration (weeks)",
            min_value=4,
            max_value=16,
            value=12,
            step=2
        )
    
    if st.button("🍂 Generate Seasonal Plan", key="seasonal_plan"):
        suggestions = generate_future_suggestions(
            filtered_df, 
            "Normal Day", 
            100,
            selected_season
        )
        
        # Display seasonal suggestions
        for suggestion in suggestions:
            if suggestion["type"] == "seasonal":
                st.markdown(f"""
                <div style='background-color: #E8F5E9; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                    <h4 style='color: #388E3C;'>🌤️ {suggestion['title']}</h4>
                    <p><strong>{suggestion['message']}</strong></p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### 🌱 Seasonal Tips:")
                for detail in suggestion["details"]:
                    st.markdown(f"• {detail}")
                
                st.markdown("#### 🎯 Seasonal Actions:")
                for action in suggestion["action_items"]:
                    st.markdown(f"✅ {action}")
        
        # Seasonal menu adjustments
        st.markdown("### 📋 Seasonal Menu Adjustments:")
        
        seasonal_categories = {
            "Summer": ["Salad", "Seafood", "Cold Meat", "Dessert"],
            "Winter": ["Fried", "Pasta", "Cake", "Main Course"],
            "Spring": ["Starter", "Salad", "Seafood"],
            "Autumn": ["Pasta", "Cake", "Fried"]
        }
        
        focus_cats = seasonal_categories.get(selected_season, [])
        
        # Show items in these categories
        seasonal_items = []
        for category in focus_cats:
            cat_items = filtered_df[filtered_df["Category"] == category]
            if len(cat_items) > 0:
                seasonal_items.extend(cat_items["Item Name"].head(2).tolist())
        
        if seasonal_items:
            st.markdown("#### 🍽️ Focus on These Items:")
            for item in seasonal_items[:6]:
                st.markdown(f"• **{item}**")
        
        # Seasonal promotion ideas
        st.markdown("#### 💡 Promotion Ideas:")
        promotion_ideas = {
            "Summer": [
                "Create 'Summer Refreshment' specials",
                "Offer cold pasta salads",
                "Feature fresh fruit desserts",
                "Promote outdoor dining options"
            ],
            "Winter": [
                "Create 'Winter Warmers' menu",
                "Offer hot chocolate with desserts",
                "Feature hearty soups and stews",
                "Promote cozy dining atmosphere"
            ]
        }
        
        ideas = promotion_ideas.get(selected_season, [])
        for idea in ideas:
            st.markdown(f"• {idea}")

with future_tab4:
    st.subheader("⚡ Quick Action Suggestions")
    
    # Current time analysis
    current_time = datetime.now()
    current_hour = current_time.hour
    
    st.info(f"""
    **🕒 Current Time: {current_time.strftime('%I:%M %p')}**
    
    Based on the time, here are your immediate actions:
    """)
    
    # Time-based actions
    if 6 <= current_hour < 11:
        st.warning("""
        **🌅 MORNING RUSH COMING!**
        
        Immediate Actions:
        1. **Prep breakfast items** - pastries, breads
        2. **Make coffee/tea stations** ready
        3. **Prep lunch ingredients** in advance
        4. **Check all equipment** is working
        5. **Review reservations** for the day
        """)
    elif 11 <= current_hour < 15:
        st.error("""
        **🔥 LUNCH RUSH ACTIVE!**
        
        Immediate Actions:
        1. **Bulk cook pasta** - make extra batches
        2. **Keep fried items** coming
        3. **Monitor buffet levels** closely
        4. **Prep dinner ingredients** between orders
        5. **Keep service fast** - focus on efficiency
        """)
    elif 17 <= current_hour < 22:
        st.error("""
        **🌙 DINNER SERVICE PEAK!**
        
        Immediate Actions:
        1. **Extra staff** on stations
        2. **Premium items** ready to go
        3. **Monitor quality** carefully
        4. **Quick replenishment** system
        5. **Dessert station** fully stocked
        """)
    else:
        st.success("""
        **🌜 OFF-PEAK HOURS**
        
        Suggested Actions:
        1. **Prep for tomorrow** - sauces, doughs
        2. **Clean and organize** stations
        3. **Inventory check** for next day
        4. **Staff training** if quiet
        5. **Menu planning** for upcoming days
        """)
    
    # Quick decision helper
    st.markdown("---")
    st.subheader("🎯 Quick Decision Helper")
    
    col_q1, col_q2 = st.columns(2)
    
    with col_q1:
        situation = st.selectbox(
            "What's happening?",
            [
                "Running low on popular item",
                "Unexpected crowd",
                "Equipment issue",
                "Staff shortage",
                "Delivery delay"
            ]
        )
    
    with col_q2:
        severity = st.select_slider(
            "Severity level",
            options=["Low", "Medium", "High", "Critical"]
        )
    
    if st.button("🆘 Get Quick Solution", key="quick_solution"):
        solutions = {
            "Running low on popular item": {
                "Low": "Make a small extra batch",
                "Medium": "Quickly prepare alternative similar item",
                "High": "Portion remaining, offer complimentary alternative",
                "Critical": "Immediately announce 'sold out', offer free dessert"
            },
            "Unexpected crowd": {
                "Low": "Add one extra staff member",
                "Medium": "Simplify menu, focus on quick items",
                "High": "Activate emergency prep, call backup staff",
                "Critical": "Implement waiting list, offer free drinks"
            },
            "Equipment issue": {
                "Low": "Use backup equipment",
                "Medium": "Modify menu to avoid affected equipment",
                "High": "Quick repair, temporary workaround",
                "Critical": "Emergency equipment rental, partial service"
            },
            "Staff shortage": {
                "Low": "Cross-train existing staff",
                "Medium": "Simplify service, focus on essentials",
                "High": "Call in backup staff, reduce menu",
                "Critical": "Limited service only, prioritize reservations"
            },
            "Delivery delay": {
                "Low": "Use substitute ingredients",
                "Medium": "Modify affected dishes",
                "High": "Create special with available ingredients",
                "Critical": "Temporarily remove items from menu"
            }
        }
        
        solution = solutions.get(situation, {}).get(severity, "Assess situation and act accordingly")
        
        st.markdown(f"""
        <div style='background-color: #FFF3E0; padding: 20px; border-radius: 10px; border-left: 5px solid #FF9800;'>
            <h4 style='color: #E65100;'>🚨 SITUATION: {situation.upper()}</h4>
            <h5 style='color: #F57C00;'>Severity: {severity}</h5>
            <p style='font-size: 18px;'><strong>IMMEDIATE ACTION:</strong></p>
            <p style='font-size: 16px; background-color: white; padding: 10px; border-radius: 5px;'>
            {solution}
            </p>
        </div>
        """, unsafe_allow_html=True)

with future_tab5:
    st.subheader("📈 Long-term Strategy")
    
    # Check if filtered_df is defined
    if 'filtered_df' not in globals() or len(filtered_df) == 0:
        st.warning("No data available. Please check your filters.")
    else:
        # Menu analysis
        st.markdown("### 📊 Menu Performance Analysis")
        
        # Calculate various metrics
        total_items = len(filtered_df)
        buffet_percentage = len(filtered_df[filtered_df["Buffet Status"] == "Present"]) / total_items * 100 if total_items > 0 else 0
        veg_percentage = len(filtered_df[filtered_df["Type"] == "Veg"]) / total_items * 100 if total_items > 0 else 0
        
        col_l1, col_l2, col_l3 = st.columns(3)
        
        with col_l1:
            st.metric("Total Menu Items", total_items)
        
        with col_l2:
            st.metric("Buffet Coverage", f"{buffet_percentage:.1f}%")
        
        with col_l3:
            st.metric("Vegetarian Items", f"{veg_percentage:.1f}%")
        
        # Category distribution chart
        st.markdown("### 📈 Category Distribution")
        
        if len(filtered_df) > 0:
            category_counts = filtered_df["Category"].value_counts()
            fig = px.bar(
                x=category_counts.index,
                y=category_counts.values,
                title="Current Category Distribution",
                labels={'x': 'Category', 'y': 'Number of Items'},
                color=category_counts.values,
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Recommendations
        st.markdown("### 💡 Long-term Recommendations")
        
        recommendations = []
        
        # 1. Menu balance
        if veg_percentage < 30 and total_items > 0:
            recommendations.append({
                "priority": "High",
                "title": "Increase Vegetarian Options",
                "reason": f"Only {veg_percentage:.1f}% vegetarian items",
                "action": "Add 3-5 new vegetarian dishes in next month"
            })
        elif veg_percentage > 70 and total_items > 0:
            recommendations.append({
                "priority": "Medium",
                "title": "Balance Vegetarian/Non-Veg",
                "reason": f"High vegetarian ratio ({veg_percentage:.1f}%)",
                "action": "Add 2-3 popular non-vegetarian specialties"
            })
        
        # 2. Buffet optimization
        if buffet_percentage < 40 and total_items > 0:
            recommendations.append({
                "priority": "High",
                "title": "Expand Buffet Options",
                "reason": f"Only {buffet_percentage:.1f}% items in buffet",
                "action": "Move 5 popular items to buffet permanently"
            })
        
        # Display recommendations
        for rec in recommendations:
            if rec["priority"] == "High":
                color = "#FFEBEE"
                icon = "🔥"
            else:
                color = "#FFF3E0"
                icon = "⚡"
            
            st.markdown(f"""
            <div style='background-color: {color}; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #FF9800;'>
                <h5>{icon} {rec['title']} <span style='font-size: 12px; color: #666;'>({rec['priority']} Priority)</span></h5>
                <p><strong>Reason:</strong> {rec['reason']}</p>
                <p><strong>Action:</strong> {rec['action']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        if not recommendations:
            st.success("✅ Your menu is well-balanced! Keep up the good work.")
        
        # Growth plan
        st.markdown("### 🚀 3-Month Growth Plan")
        
        growth_steps = [
            {"month": 1, "focus": "Menu Optimization", "actions": ["Analyze sales data", "Remove low-performing items", "Add 3 new seasonal items"]},
            {"month": 2, "focus": "Staff Training", "actions": ["Cross-training program", "Quality standards workshop", "Efficiency improvements"]},
            {"month": 3, "focus": "Customer Experience", "actions": ["Introduce special menus", "Improve presentation", "Gather customer feedback"]}
        ]
        
        for step in growth_steps:
            with st.expander(f"📅 Month {step['month']}: {step['focus']}"):
                for action in step["actions"]:
                    st.checkbox(action)

# ============================================================
# SPECIFIC ITEM SUGGESTIONS
# ============================================================
st.markdown("---")
st.subheader("🍽️ Specific Item Cooking Suggestions")

# Get buffet items
buffet_items = filtered_df[filtered_df["Buffet Status"] == "Present"]

if len(buffet_items) > 0:
    # Group by category
    categories = buffet_items["Category"].unique()
    
    for category in categories[:3]:  # Show first 3 categories
        category_items = buffet_items[buffet_items["Category"] == category]
        
        with st.expander(f"📁 {category} Items ({len(category_items)} items)"):
            for idx, item in category_items.iterrows():
                # Category-specific suggestions
                if category == "Fried":
                    suggestion = f"""
                    **{item['Item Name']}** ({item['Type']})
                    - Cook extra: 30% more than estimated
                    - Timing: Fry in small batches 30 minutes before service
                    - Tip: Keep oil at 180°C for perfect crispiness
                    - Hold time: 1 hour maximum
                    """
                elif category == "Pasta":
                    suggestion = f"""
                    **{item['Item Name']}** ({item['Type']})
                    - Cook extra: 40% more than estimated
                    - Timing: Cook pasta 1 hour before, keep sauce separate
                    - Tip: Shock pasta in ice water to stop cooking
                    - Hold time: 2 hours (with sauce separately)
                    """
                elif category == "Cake":
                    suggestion = f"""
                    **{item['Item Name']}** ({item['Type']})
                    - Cook extra: 20% more than estimated
                    - Timing: Bake day before, decorate day of
                    - Tip: Store in airtight containers
                    - Hold time: 3 days
                    """
                else:
                    suggestion = f"""
                    **{item['Item Name']}** ({item['Type']})
                    - Cook extra: 25% more than estimated
                    - Timing: Prepare 2 hours before service
                    - Tip: Monitor temperature carefully
                    - Hold time: 2-3 hours
                    """
                
                st.markdown(suggestion)
                st.markdown("---")
else:
    st.info("👈 Select buffet items to see specific cooking suggestions")

# ============================================================
# FINAL SUMMARY
# ============================================================
st.markdown("---")
st.subheader("🎯 SUMMARY OF KEY SUGGESTIONS")

col_sum1, col_sum2 = st.columns(2)

with col_sum1:
    st.markdown("""
    ### 🔥 IMMEDIATE ACTIONS:
    1. **Check inventory** of popular items
    2. **Prep stations** for today's service
    3. **Review today's reservations**
    4. **Brief staff** on specials
    5. **Quality check** all stations
    """)

with col_sum2:
    st.markdown("""
    ### 📈 FUTURE FOCUS:
    1. **Monitor sales** patterns
    2. **Adjust quantities** based on demand
    3. **Experiment** with new items
    4. **Train staff** on new techniques
    5. **Gather customer feedback**
    """)

st.success("""
**👨‍🍳 CHEF READY!** 
All suggestions generated. Use these insights to plan your cooking and improve service!
""")

# ============================================================
# HOW TO RUN
# ============================================================
