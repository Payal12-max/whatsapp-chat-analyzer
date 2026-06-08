import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns


col1, col2 = st.columns([2,1])

with col1:
    st.markdown("""
<h1 style='font-size:70px;font-weight:800;color:beige;'>
 WhatsApp Insights
</h1>

<p style='font-size:22px;color:white;'>
Transform thousands of messages into beautiful analytics,
interactive visualizations, and actionable insights.
</p>
""", unsafe_allow_html=True)
st.markdown("""
<style>
[data-testid="stImage"] img {
    border: 4px solid white;
    border-radius: 20px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.25);
}
</style>
""", unsafe_allow_html=True)
with col2:
    st.image(
        "images/banner.png",
        width=300,
    )

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    page_icon="💬",
    layout="wide"
)

# ================= CSS =================
st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        green 0%,
        white 100%
    );
}

h1 {
    color: green;
}

</style>
""", unsafe_allow_html=True)

# ================= HEADER =================

st.markdown("""
<style>

/* File uploader container */
[data-testid="stFileUploader"] {
    background: white;
    padding: 20px;
    border-radius: 20px;
    border: 2px dashed #25D366;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

/* Upload button */
[data-testid="stFileUploader"] button {
    background-color: #25D366 !important;
    color: white !important;
    border-radius: 10px !important;
    border: none !important;
    font-weight: bold !important;
}

/* Hover effect */
[data-testid="stFileUploader"] button:hover {
    background-color: #128C7E !important;
}

/* Drag area */
[data-testid="stFileUploaderDropzone"] {
    border: 2px dashed #25D366 !important;
    border-radius: 15px !important;
    background-color: #f8fff9 !important;
}

</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
st.sidebar.title(" Chat Analyzer")

uploaded_file = st.sidebar.file_uploader(
    "Choose WhatsApp Chat Export"
)

if uploaded_file is not None:

    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")

    df = preprocessor.preprocess(data)

    with st.expander(" View Processed Data"):
        st.dataframe(df.head(20))

    # USERS
    user_list = df['user'].unique().tolist()

    if 'group_notification' in user_list:
        user_list.remove('group_notification')

    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox(
        "Show Analysis For",
        user_list
    )

    if st.sidebar.button(" Analyze Chat"):

        # ================= STATS =================

        num_messages, words, media, links = helper.fetch_stats(
            selected_user,
            df
        )

        st.markdown("##  Top Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(" Messages", num_messages)

        with col2:
            st.metric(" Words", words)

        with col3:
            st.metric(" Media", media)

        with col4:
            st.metric(" Links", links)

        # ================= TABS =================

        tab1, tab2, tab3, tab4 = st.tabs([
            " Timeline",
            " Activity",
            " WordCloud",
            " Emoji Analysis"
        ])

        # =====================================================
        # TIMELINE TAB
        # =====================================================

        with tab1:

            st.subheader("Monthly Timeline")

            timeline = helper.monthly_timeline(
                selected_user,
                df
            )

            fig, ax = plt.subplots(figsize=(10,5))

            ax.plot(
                timeline['time'],
                timeline['message'],
                marker='o',
                linewidth=3
            )

            plt.xticks(rotation=45)

            st.pyplot(fig)

            st.subheader("Daily Timeline")

            daily_timeline = helper.daily_timeline(
                selected_user,
                df
            )

            fig, ax = plt.subplots(figsize=(10,5))

            ax.plot(
                daily_timeline['only_date'],
                daily_timeline['message']
            )

            plt.xticks(rotation=45)

            st.pyplot(fig)

        # =====================================================
        # ACTIVITY TAB
        # =====================================================

        with tab2:

            col1, col2 = st.columns(2)

            with col1:

                st.subheader("Most Busy Day")

                busy_day = helper.week_activity_map(
                    selected_user,
                    df
                )

                fig, ax = plt.subplots()

                ax.bar(
                    busy_day.index,
                    busy_day.values
                )

                plt.xticks(rotation=45)

                st.pyplot(fig)

            with col2:

                st.subheader("Most Busy Month")

                busy_month = helper.month_activity_map(
                    selected_user,
                    df
                )

                fig, ax = plt.subplots()

                ax.bar(
                    busy_month.index,
                    busy_month.values
                )

                plt.xticks(rotation=45)

                st.pyplot(fig)

            st.subheader("Weekly Heatmap")

            user_heatmap = helper.activity_heatmap(
                selected_user,
                df
            )

            if not user_heatmap.empty:

                fig, ax = plt.subplots(figsize=(12,6))

                sns.heatmap(
                    user_heatmap,
                    ax=ax
                )

                st.pyplot(fig)

            else:
                st.warning(
                    "No data available for heatmap."
                )

            if selected_user == "Overall":

                st.subheader("Most Busy Users")

                x, new_df = helper.most_busy_users(df)

                col1, col2 = st.columns(2)

                with col1:

                    fig, ax = plt.subplots()

                    ax.bar(
                        x.index,
                        x.values
                    )

                    plt.xticks(rotation=45)

                    st.pyplot(fig)

                with col2:
                    st.dataframe(new_df)

        # =====================================================
        # WORD CLOUD TAB
        # =====================================================

        with tab3:

            st.subheader("Word Cloud")

            wc = helper.create_wordcloud(
                selected_user,
                df
            )

            if wc is not None:

                fig, ax = plt.subplots(
                    figsize=(8,6)
                )

                ax.imshow(wc)

                ax.axis("off")

                st.pyplot(fig)

            else:
                st.warning(
                    "No words available."
                )

            st.subheader("Most Common Words")

            common_df = helper.most_common_words(
                selected_user,
                df
            )

            if not common_df.empty:

                fig, ax = plt.subplots(
                    figsize=(8,6)
                )

                ax.barh(
                    common_df.iloc[:,0],
                    common_df.iloc[:,1]
                )

                st.pyplot(fig)

            else:
                st.warning(
                    "No common words found."
                )

        # =====================================================
        # EMOJI TAB
        # =====================================================

        with tab4:

            emoji_df = helper.emoji_helper(
                selected_user,
                df
            )

            col1, col2 = st.columns(2)

            with col1:
                st.dataframe(emoji_df)

            with col2:

                if not emoji_df.empty:

                    fig, ax = plt.subplots()

                    ax.pie(
                        emoji_df.iloc[:5,1],
                        labels=emoji_df.iloc[:5,0],
                        autopct="%0.2f%%"
                    )

                    st.pyplot(fig)

                else:
                    st.warning(
                        "No emojis found."
                    )