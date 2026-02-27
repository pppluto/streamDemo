import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# 1. 定义中英文对照字典 (在这里添加你想要翻译的所有列名)
    # 格式： '英文原名': '中文显示名'
col_map = {
    # 基础信息
    'HTML': '素材名称',
    'URL': '链接地址',
        
    # 核心消耗与展示
    'Impressions': '展示量 (Impressions)',
    'Spend': '花费金额 (Spend)',
    'Share of Spend': '花费占比',
        
    # 互动与转化 (核心KPI)
    'Unique redirects': '唯一跳转人数',
    'Unique interactions': '唯一互动人数',
    'Total interactions': '总互动次数',
    'CTA clicked': '点击按钮次数 (CTA Clicked)',
    'Redirect count': '总跳转次数',
        
    # 核心转化率
    'Unique redirects rate': '跳转转化率 (CVR)',
    'Unique interactions rate': '互动率 (IVR)',
    'CTA click rate': '点击率 (CTR)',
    'Redirect rate': '总跳转率',
        
    # 页面加载与生命周期
    'Average duration': '平均停留时长 (秒)',
    'HTML loading': '开始加载次数',
    'HTML loaded': '加载完成次数',
    'HTML displayed': '成功展示次数',
    'HTML completed': '试玩结束次数',
    'HTML completion rate': '完播率/完成率',
    'Endcard shown': '落地页展示次数',
        
    # 游戏内行为 (漏斗)
    'Challenge started': '游戏开始次数',
    'Challenge failed': '游戏失败次数',
    'Challenge retry': '游戏重试次数',
    'Challenge solved': '游戏通关次数',
    'Challenge pass 25': '进度达25%次数',
    'Challenge pass 50': '进度达50%次数',
    'Challenge pass 75': '进度达75%次数',
        
    # 游戏内比率
    'Challenge failed rate': '游戏失败率 (Failure Rate)',
    'Challenge retry rate': '游戏重试率 (Retry Rate)',
    'Challenge solved rate': '游戏通关率 (Win Rate)',
    'Challenge pass 25 rate': '25%进度达成率',
    'Challenge pass 50 rate': '50%进度达成率',
    'Challenge pass 75 rate': '75%进度达成率',
        
    # 技术报错 (Debug)
    'Black view error': '黑屏错误数',
    'Rendering error': '渲染错误数',
    'Runtime error': '运行错误数',
    'Black view error rate': '黑屏率',
    'Rendering error rate': '渲染错误率',
    'Runtime error rate': '运行报错率'
}
    # 一个辅助函数：如果有翻译就用翻译，没有就显示原文
def get_label(col_name):
    return col_map.get(col_name, col_name)

st.set_page_config(layout="wide")
st.title("📊 广告数据看板 (本地读取)")

#侧边栏
with st.sidebar:
    st.header("📍 页面导航")
    page = st.radio("选择功能模块", ["📊 数据看板", "🛠️ 自定义探索"], index=0)
    st.markdown("---")


    st.header("⚙️ 参数设置")
    file_name = st.text_input("Excel 文件名", value="sksx.xlsx")
    min_imp = st.number_input("展示量过滤最小阈值 (Impressions > ?)", value=1000, step=100)
    max_imp = st.number_input("展示量过滤最大阈值 (Impressions < ?)", value=-1, step=100)
    if st.button("🔄 刷新数据"):
        st.rerun()


try:
    df = pd.read_excel(file_name, engine='openpyxl')
    st.success("✅ 本地文件 'sksx.xlsx' 读取成功！")
    
except FileNotFoundError:
    st.error("❌ 找不到文件！请确认 'sksx.xlsx' 在当前目录下。")
    st.stop()
except Exception as e:
    st.error(f"❌ 读取失败！文件被加密")
    st.stop()


st.success("🎉 读取成功！")

#筛选有效数据 默认展示量过滤阈值为1000 可自行修改
if max_imp > 0 and max_imp > min_imp:
    df_effective = df[(df['Impressions'] >  min_imp) & (df['Impressions'] <  max_imp) & (df['CTA clicked'] != 0)]
else:
    df_effective = df[(df['Impressions'] >  min_imp) & (df['CTA clicked'] != 0)]

with st.sidebar:
    st.markdown("---") 
    st.header("🔎 素材链接搜索")
    search_keyword = st.text_input("输入素材名 (如果不填默认显示Top20)", "")
    df_search = df_effective.sort_values(by='Impressions', ascending=False)[['HTML', 'URL']].drop_duplicates()
    
    if search_keyword:
        df_display_links = df_search[df_search['HTML'].str.contains(search_keyword, case=False, na=False)]
    else:
        df_display_links = df_search.head(20)
    max_items = 20
    if len(df_display_links) > max_items:
        st.warning(f"结果太多，仅显示前 {max_items} 条...")
        df_display = df_display_links.head(max_items)
    else:
        df_display = df_display_links

    if not df_display.empty:
        for index, row in df_display.iterrows():
            with st.container(border=True): 
                st.markdown(f"<div style='font-size:12px; word-break:break-all;'><b>{row['HTML']}</b></div>", unsafe_allow_html=True)

                st.link_button("👉 点击试玩", row['URL'], use_container_width = True)
    else:
        st.caption("没有找到匹配的素材")
st.write("前5行数据预览（用于确保数据读取正确）", df.head())
st.write('注：为了确保数据分析有效，默认选取数据中Impression值>1000,且有正常埋点触发逻辑（即CTA clicked值>0）的可玩素材进行分析，如需修改Impression值请自行调整左侧展示量过滤阈值。')

#清洗点击量过于低的数据  以及没有埋点数据的素材（这类素材由于制作过早 并没有埋点触发的逻辑 缺少大量数据 因此目前暂不计入分析）
st.markdown("---")
if page == "📊 数据看板":
    st.header("📊 数据看板")
    st.caption("一目了然获取到你所想要了解的数据信息。")
    
    #获取有明确游戏结果的游戏以及限时自由游戏
    df_haveResultGame = df_effective[(df_effective['Challenge solved'] > 50) & (df_effective['Challenge failed'] > 50 )]
    df_freeTimeGame = df_effective[(df_effective['Challenge solved'] == 0) & (df_effective['Challenge failed'] == 0 )]
    #获取更具体一步的数据
    #前十名 展示量游戏
    top10_impressionsGames = df_effective.sort_values(by = 'Impressions' , ascending = False).head(10)
    #前十名完成率较低的游戏
    top10_imcompleteGames = df_haveResultGame.copy()
    top10_imcompleteGames['Incomplete Count'] = top10_imcompleteGames['Challenge started'] - top10_imcompleteGames['Challenge solved'] - top10_imcompleteGames['Challenge failed']
    top10_imcompleteGames['Incomplete Rate'] = top10_imcompleteGames['Incomplete Count'] / top10_imcompleteGames['Challenge started']
    top10_imcompleteGames = top10_imcompleteGames.sort_values(by = 'Incomplete Rate',ascending = False).head(10)
    #前五名最困难的游戏
    top5_hardGames = df_haveResultGame.sort_values(by = 'Challenge failed rate' , ascending= False).head(5)
    #前五名最容易的游戏
    top5_easyGames = df_haveResultGame.sort_values(by = 'Challenge solved rate' , ascending= False).head(5)
    #前五名运行中错误率最高的素材
    top5_errorGames = df_effective.sort_values(by = 'Runtime error rate',ascending = False).head(5)



    #数据卡 展示总数据量
    st.subheader("核心指标概览")
    # 使用列布局，让卡片横向排列
    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)
    with c1:
        # label: 标题
        # value: 大数字 (字符串)
        # delta: 变化量 (绿色向上箭头，负数自动变红向下)
        st.metric(
            label="总展示量 (Impressions)", 
            value= df["Impressions"].sum(), 
        )
    with c2:
        st.metric(
            label="总花费 (Spend)", 
            value= "$" + f"{df["Spend"].sum():,.2f}", 
        )
    with c3:
        st.metric(
            label="平均点击率（CTR）", 
            value= f"{df["CTA click rate"].mean():.2%}", 
        )
    with c4:
        st.metric(
            label="转化数 (Conversions)", 
            value= df["CTA clicked"].sum(), 
        )



    #柱状图 Top10 展示量最高的游戏数据展示

    fig_impressionsGames = px.bar(
        top10_impressionsGames,
        title= '柱状图：Top10 展示量最高的游戏 (鼠标悬停看详情)',
        x='HTML',
        y=['Impressions', 'CTA clicked','Unique interactions','Total interactions','Redirect count'], 
        barmode='group', 
        text_auto='.2s',
        hover_data = ['CTA click rate'],
        labels={
            'HTML': '素材',
        }
    )
    fig_impressionsGames.update_yaxes(type="log", title_text="数量 (次)") 
    fig_impressionsGames.update_layout(legend_title_text='数据指标' )
    new_names = {
        'Impressions': '展示量（次）',
        'CTA clicked': '点击量（次）',
        'Unique interactions':'唯一交互人数',
        'Total interactions':'总交互次数',
        'Redirect count':'跳转总次数'
    }
    fig_impressionsGames.for_each_trace(lambda t: t.update(name = new_names[t.name]))
    fig_impressionsGames.update_layout(template='seaborn')
    st.plotly_chart(fig_impressionsGames)



    #柱状图 Top10 流失率最高的游戏

    fig_imcompleteGames = px.bar(
        top10_imcompleteGames,
        title = '柱状图：流失率（指未完成整个游戏流程）最高 Top10 的可玩',
        x = 'HTML',
        y = ['Incomplete Rate','Challenge solved rate','Challenge failed rate'],
        barmode = 'group',
        text_auto='.2%',
        hover_data = ['Impressions'],
        labels={
            'HTML': '素材',
            'Incomplete Rate':'未完率'
        }
    )
    new_names = {
        'Incomplete Rate':'未完率',
        'Challenge failed rate':'失败率',
        'Challenge solved rate':'成功率'
    }
    fig_imcompleteGames.update_yaxes(type="log", title_text="数量 (次)") 
    fig_imcompleteGames.for_each_trace(lambda t: t.update(name = new_names[t.name]))
    fig_imcompleteGames.update_layout(template='seaborn')
    st.plotly_chart(fig_imcompleteGames)



    #柱状图 Top5 最困难的可玩游戏的数据展示

    col_left, col_right = st.columns(2)
    with col_left:
        #开启双侧尺
        fig_hardGames = make_subplots(specs=[[{"secondary_y": True}]])
        #添加第一个柱状图 使用左侧轴
        fig_hardGames.add_trace(
            go.Bar(
                x=top5_hardGames['HTML'],
                y=top5_hardGames['Impressions'],
                name='展示量 (Impressions)',   
                marker_color='#636EFA', 
                opacity=0.6,     
                offsetgroup=1 
            ),
            secondary_y = False 
        )
        #添加第二个柱状图 使用左侧轴
        fig_hardGames.add_trace(
            go.Bar(
                x=top5_hardGames['HTML'], 
                y=top5_hardGames['CTA clicked'],
                name='点击量 (CTA Clicked)',
                marker_color='#EF553B', 
                offsetgroup=2 
            ),
            secondary_y=False
        )
        #添加折线图 使用右侧轴
        fig_hardGames.add_trace(
            go.Scatter(
                x=top5_hardGames['HTML'],
                y=top5_hardGames['Challenge failed rate'],
                name='失败率 (Rate)',
                mode='lines+markers+text',
                marker=dict(size=10, color='green'), # 绿色点
                text=top5_hardGames['Challenge failed rate'],
                texttemplate='%{text:.1%}', 
                textposition='top center'
            ),
            secondary_y=True # 这一根线走右边的轴
        )
        fig_hardGames.update_layout(
            title='柱状折线图：Top5 最困难的可玩',
            barmode='group' # 让柱子成簇排列
        )
        fig_hardGames.update_yaxes(title_text="数量 (次)", secondary_y=False)
        fig_hardGames.update_yaxes(title_text="比率 (%)", tickformat=".0%", secondary_y=True)
        fig_hardGames.update_layout(template='seaborn')
        st.plotly_chart(fig_hardGames)



    #柱状折线图 Top5 最容易的可玩数据展示

    #开启双侧尺
    with col_right:
        fig_easyGames = make_subplots(specs=[[{"secondary_y": True}]])
        #添加第一个柱状图 使用左侧轴
        fig_easyGames.add_trace(
            go.Bar(
                x = top5_easyGames['HTML'],
                y = top5_easyGames['Impressions'],
                name = '展示量 (Impressions)',   
                marker_color = '#636EFA', 
                opacity = 0.6,     
                offsetgroup = 1 
            ),
            secondary_y = False 
        )
        #添加第二个柱状图 使用左侧轴
        fig_easyGames.add_trace(
            go.Bar(
                x = top5_easyGames['HTML'], 
                y = top5_easyGames['CTA clicked'],
                name = '点击量 (CTA Clicked)',
                marker_color = '#EF553B', 
                offsetgroup = 2 
            ),
            secondary_y = False
        )
        #添加折线图 使用右侧轴
        fig_easyGames.add_trace(
            go.Scatter(
                x = top5_easyGames['HTML'],
                y = top5_easyGames['Challenge solved rate'],
                name = '成功率 (Rate)',
                mode = 'lines+markers+text',
                marker = dict(size=10, color='green'), # 绿色点
                text = top5_easyGames['Challenge solved rate'],
                texttemplate = '%{text:.1%}', 
                textposition = 'top center'
            ),
            secondary_y = True # 这一根线走右边的轴
        )
        fig_easyGames.update_layout(
            title='柱状折线图：Top5 最容易的可玩',
            barmode='group' # 让柱子成簇排列
        )
        fig_easyGames.update_yaxes(type="log", secondary_y=False)
        fig_easyGames.update_yaxes(title_text="数量 (次)", secondary_y=False)
        fig_easyGames.update_yaxes(title_text="比率 (%)", tickformat=".0%", secondary_y=True)
        fig_easyGames.update_layout(template='seaborn')
        st.plotly_chart(fig_easyGames)



    #散点图 平均停留时长和转化率之间的关系

    fig_impressionsAndCTA = px.scatter(
        df_effective,
        title='散点图：玩家平均停留时长 vs 转化率关联分析 (气泡越大，颜色越深，平均停留时长越长)',
        x='Average duration',    # X轴: 玩家平均停留时长
        y='Unique redirects rate',      # Y轴：转化率
        size='Average duration',             # 气泡大小：玩家平均停留时长越长 气泡越大
        color='Average duration',  # 颜色：展示量越大 越绿
        color_continuous_scale= 'Greens',
        trendline="ols",                
        labels={
            'Average duration': '玩家平均停留时长（秒）',
            'Unique redirects rate': '转化效果 (跳转率)'
        }
    )
    fig_impressionsAndCTA.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
    fig_impressionsAndCTA.update_layout(template='seaborn')
    st.plotly_chart(fig_impressionsAndCTA)



    #散点图 展示游戏难度和转化率之间的关系

    fig_diffcultyAndCTA = px.scatter(
        df_haveResultGame,
        title='散点图：游戏难度 vs 转化率关联分析 (气泡越大，展示量越大，颜色越深，难度越高)',
        x='Challenge failed rate',      # X轴：难度 (失败率)    
        y='Unique redirects rate',      # Y轴：转化率
        size='Impressions',             # 气泡大小：展示量
        color='Challenge failed rate',  # 颜色：越红越难
        color_continuous_scale= 'YlOrBr',
        # 鼠标悬停显示素材名，方便你抓出那个“特异点”是谁
        hover_name='HTML',              
        # 【关键】加一条趋势线 (OLS回归线)
        # 如果运行报错，说明没装 statsmodels 库，删掉这行即可
        trendline="ols",                
        labels = {
            'Challenge failed rate': '难度 (失败率)',
            'Unique redirects rate': '转化效果 (跳转率)'
        }
    )
    fig_diffcultyAndCTA.update_traces(marker=dict(sizemin=5)) 
    fig_diffcultyAndCTA.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
    fig_diffcultyAndCTA.update_layout(xaxis_tickformat=".0%", yaxis_tickformat=".1%")
    fig_diffcultyAndCTA.update_layout(template='seaborn')
    st.plotly_chart(fig_diffcultyAndCTA)



    #散点图：人均操作次数 (Interaction Intensity) vs 点击转化率 (CTR) 关联分析

    df_interaction_analysis = df_effective[(df_effective['Unique interactions'] > 0)].copy()
    df_interaction_analysis['Clicks per User'] = df_interaction_analysis['Total interactions'] / df_interaction_analysis['Unique interactions']
    df_filtered = df_interaction_analysis[
        (df_interaction_analysis['Clicks per User'] >= 1) & 
        (df_interaction_analysis['Clicks per User'] <= 50)
    ]
    fig_correlation = px.scatter(
        df_filtered,
        title='散点图：人均操作次数 vs 转化率关联分析（气泡越大，展示量越大，颜色越深，人均操作量越高）',
        x='Clicks per User',      
        y='CTA click rate',       
        size='Impressions',             # 气泡越大，说明该数据点越可靠（样本量大）
        color='Clicks per User',        # 颜色仅仅为了好看区分

        trendline="lowess",             
        
        hover_name='HTML',              # 鼠标悬停显示素材名，方便抓典型
        hover_data={
            'Impressions': ':.2s',      # 格式化展示量
            'Clicks per User': ':.1f',  # 保留1位小数
            'CTA click rate': ':.2%'    # 百分比格式
        },
        labels={
            'Clicks per User': '人均操作次数 (强度)',
            'CTA click rate': '点击转化率 (CTR)'
        }
    )
    fig_correlation.update_layout(
        yaxis_tickformat=".1%",
        template='seaborn',
        legend_title="操作强度"
    )
    best_performer = df_filtered.loc[df_filtered['CTA click rate'].idxmax()]
    best_clicks = best_performer['Clicks per User']
    best_ctr = best_performer['CTA click rate']
    fig_correlation.add_annotation(
        x=best_clicks,
        y=best_ctr,
        text=f"巅峰转化: {best_ctr:.1%} (需操作 {best_clicks:.1f} 次)",
        showarrow=True,
        arrowhead=1,
        ax=0,
        ay=-40
    )
    fig_correlation.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
    fig_correlation.update_traces(marker=dict(sizemin=5)) 
    st.plotly_chart(fig_correlation)



    #漏斗图 1：总体转化链路 (曝光 -> 展示 -> 开始 -> 完成 -> 点击)

    funnel_cols = ['Impressions', 'HTML displayed', 'Challenge started', 'Challenge solved', 'CTA clicked']
    funnel_values = df_effective[funnel_cols].sum()
    fig_funnel_total = go.Figure(go.Funnel(
        y = ['曝光 (Impressions)', '成功展示 (Displayed)', '开始游戏 (Started)', '游戏通关 (Solved)', '点击转化 (CTA Clicked)'],
        x = funnel_values.values,
        textinfo = "value+percent previous",  # 显示数值 + 占上一步的百分比
        opacity = 0.65,
        marker = {"color": ["#1f77b4", "#00b3ca", "#ff7f0e", "#2ca02c", "#d62728"]},
        connector = {"line": {"color": "royalblue", "dash": "dot", "width": 3}}
    ))

    fig_funnel_total.update_layout(
        title_text="漏斗图：总体用户转化漏斗 (基于清洗后数据)", 
        template='seaborn'
    )
    st.plotly_chart(fig_funnel_total)



    #漏斗图 2：游戏内深度流失分析 (开始 -> 25% -> 50% -> 75% -> 通关)

    game_depth_cols = ['Challenge started', 'Challenge pass 25', 'Challenge pass 50', 'Challenge pass 75', 'Challenge solved']
    game_depth_values = df_effective[game_depth_cols].sum()
    fig_funnel_game = go.Figure(go.Funnel(
        y = ['开始游戏', '进度 25%', '进度 50%', '进度 75%', '通关 (Solved)'],
        x = game_depth_values.values,
        textinfo = "value+percent initial", # 这里推荐看“占初始值(开始游戏)的百分比”，即留存率
        marker = {"color": "#636efa"},
        connector = {"line": {"color": "white", "width": 2}}
    ))
    fig_funnel_game.update_layout(
        title_text="漏斗图：游戏内玩家流失详情 (留存分析)", 
        template='seaborn'
    )
    st.plotly_chart(fig_funnel_game)



    #直方图：用户平均交互次数分布 (Interaction Intensity)

    df_interaction = df_effective[df_effective['Unique interactions'] > 0].copy()
    df_interaction['Clicks per User'] = df_interaction['Total interactions'] / df_interaction['Unique interactions']

    fig_interact = px.histogram(
        df_interaction,
        title='直方图：用户平均点击/滑动次数分布',
        x='Clicks per User',
        nbins= 20, # 分成20个区间
        marginal= "box", # 顶部显示箱线图，看中位数
        color_discrete_sequence=['#AB63FA'
    ],
        labels={'Clicks per User': '平均每人操作次数'}
    )

    fig_interact.update_layout(
        bargap=0.1, 
        template='seaborn',
        xaxis_title="每人平均操作次数", 
        yaxis_title="素材数量 (个)"
    )
    st.plotly_chart(fig_interact)


    #直方图：展示玩家的集中停留时长

    # 取出有效数据列，防止报错
    df_dist = df_effective[['Average duration']].dropna()
    # 创建直方图 + 密度曲线 (marginal='box' 顶部加箱线图辅助)
    fig_hist = px.histogram(
        df_dist, 
        x="Average duration",
        nbins=30,  
        marginal="box",
        opacity=0.75,
        title="直方图：大部分用户的停留时长分布",
        labels={"Average duration": "停留时长 (秒)"},
        color_discrete_sequence=['#636EFA'] 
    )
    mean_val = df_dist['Average duration'].mean()
    fig_hist.add_vline(
        x=mean_val, 
        line_dash="dash", 
        line_color="red", 
        annotation_text=f"平均值: {mean_val:.1f}s"
    )
    p99 = df_dist['Average duration'].quantile(0.99)
    fig_hist.update_xaxes(range=[0, p99])
    fig_hist.update_layout(
        bargap=0.1, 
        template='seaborn',
        yaxis_title="用户/素材数量 (个)"
    )
    st.plotly_chart(fig_hist, use_container_width=True)


if page == "🛠️ 自定义探索":
    import time
    t0 = time.time()
    print("进入沙盒页")
    st.header("🛠️ 自定义数据探索 (沙盒模式)")
    st.caption("在此处随机组合数据，探索未知的可能性以及趋势。")
    st.write('''注： 
    \n柱状图：可用于展示比较不同素材之间的某些指标
    \n散点图：可用于展示数据之间的关联关系
    \n直方图：可用于展示数据的分布情况
    ''')
    
    # 1. 准备数据列分类
    all_columns = df_effective.columns.tolist()
    numeric_columns = df_effective.select_dtypes(include=['float64', 'int64']).columns.tolist()
    string_columns = df_effective.select_dtypes(include=['object', 'string', 'category']).columns.tolist()

    # 2. 布局：增加 "直方图/密度图" 选项
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        # >>> 修改点：增加了选项 <<<
        chart_type = st.selectbox("图表类型", ["散点图", "柱状图", "直方图"])
    with c2:
        data_show_num = st.number_input("展示数据量 (Top N)", value=1000, step=100, min_value=10) 
        # 注：可以把默认值改大一点，看分布需要较多数据

    st.markdown("---")
    
    # 3. 动态选项区
    col1, col2, col3 = st.columns(3)
    # 初始化变量
    x_axis_val, y_axis_val, z_axis_val = None, None, None
    color_group = None # 专门给直方图用的分组变量
     # --- A: 散点图 ---
    if chart_type == "散点图":
        with col1:
            idx_x = numeric_columns.index('Impressions') if 'Impressions' in numeric_columns else 0
            x_axis_val = st.selectbox("X 轴 (仅数值)", numeric_columns, index=idx_x, format_func=get_label)
        with col2:
            idx_y = numeric_columns.index('CTA click rate') if 'CTA click rate' in numeric_columns else 0
            y_axis_val = st.selectbox("Y 轴 (仅数值)", numeric_columns, index=idx_y, format_func=get_label)
        with col3:
            z_axis_val = st.selectbox("气泡大小 (可选)", ['无'] + numeric_columns, format_func=lambda x: "无" if x == '无' else get_label(x))

    # --- B: 柱状图 ---
    elif chart_type == "柱状图":
        with col1:
            default_str = 'HTML' if 'HTML' in string_columns else (string_columns[0] if string_columns else None)
            x_axis_val = st.selectbox("X 轴 (素材/分组)", string_columns, index=string_columns.index(default_str) if default_str else 0, format_func=get_label)
        with col2:
            default_y = [c for c in ['Impressions', 'CTA clicked'] if c in numeric_columns]
            if not default_y: default_y = [numeric_columns[0]]
            y_axis_val = st.multiselect("Y 轴 (数值 - 支持多选)", numeric_columns, default=default_y, format_func=get_label)

    # --- C: 直方图 ---
    elif chart_type == "直方图":
        with col1:
            idx_target = numeric_columns.index('CTA click rate') if 'CTA click rate' in numeric_columns else 0
            x_axis_val = st.selectbox("分析指标 (数值)", numeric_columns, index=idx_target, format_func=get_label)
        with col2:
            color_group = st.selectbox("分组依据 (可选)", ["无"] + string_columns, format_func=lambda x: "无 (整体分布)" if x == "无" else get_label(x))
        with col3:
            marginal_type = st.selectbox("顶部附图", ["box", "violin", "rug", "None"], index=0, format_func=lambda x: {"box":"箱型图", "violin":"小提琴图", "rug":"密度条", "None":"无"}[x])
            show_kde = st.checkbox("显示平滑密度曲线", value=True)
    # 绘图逻辑
    if x_axis_val: 
        st.subheader(f"📈 分析图表")
        
        # 数据截取
        if data_show_num > 0:
            df_show = df_effective.head(data_show_num).copy()
        else:
            df_show = df_effective.copy()
            
        try:
            # --- 绘图 A：散点图 ---
            if chart_type == "散点图" and y_axis_val:
                df_show = df_show.dropna(subset=[x_axis_val, y_axis_val])
                plot_args = {
                    "data_frame": df_show,
                    "x": x_axis_val,
                    "y": y_axis_val,
                    "hover_name": "HTML",
                    "height": 600,
                    "labels": col_map, # 关键：传入字典实现自动翻译
                    "template": "seaborn",
                    "trendline": "ols",
                    "render_mode": "webgl"
                }
                if z_axis_val != '无':
                    plot_args["size"] = z_axis_val
                    plot_args["color"] = z_axis_val # 气泡颜色随大小变化更直观
                
                fig = px.scatter(**plot_args)
                fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))

            # --- 绘图 B：柱状图 ---
            elif chart_type == "柱状图" and y_axis_val:
                sort_col = y_axis_val[0] if isinstance(y_axis_val, list) else y_axis_val
                df_show = df_show.sort_values(by=sort_col, ascending=False)
                fig = px.bar(
                    df_show,
                    x=x_axis_val, y=y_axis_val,
                    barmode='group', height=600,
                    labels=col_map, # 关键：翻译
                    template="seaborn"
                )

            # --- 绘图 C：直方图/密度图 ---
            elif chart_type == "直方图":
                # 参数准备
                color_arg = None if color_group == "无" else color_group
                barmode_arg = 'overlay' if color_arg else 'relative'
                marginal_arg = None if marginal_type == "None" else marginal_type
                
                fig = px.histogram(
                    df_show,
                    x=x_axis_val,      # 分析的数值
                    color=color_arg,   # 分组颜色
                    marginal=marginal_arg, # 顶部显示箱型图
                    hover_name="HTML",
                    height=600,
                    labels=col_map,    # 关键：翻译
                    template="seaborn",
                    opacity=0.75,      # 透明度，方便看重叠
                    barmode=barmode_arg,
                    histnorm='probability density' if show_kde else None, # 如果要看KDE线，y轴最好是密度
                    nbins=50
                )
                
                # Plotly Express 暂时无法直接一条命令加 KDE 曲线覆盖在直方图上
                # 但可以通过 histnorm 配合 update_traces 让直方图更有“密度感”
                # 如果非常需要平滑曲线，通常做法较为复杂，此处用直方+箱型图其实对于业务分析已经足够清晰
                
                # 优化 X/Y 轴显示标题 (防止 Plotly 偶尔不读取 labels)
                fig.update_layout(
                    xaxis_title=get_label(x_axis_val),
                    yaxis_title="概率密度 (Density)" if show_kde else "频次 (Count)"
                )

                if barmode_arg == 'overlay':
                    fig.update_layout(title=f"《{get_label(x_axis_val)}》分布对比 (按 {get_label(color_arg)} 分组)")
                else:
                    fig.update_layout(title=f"《{get_label(x_axis_val)}》整体分布")

            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"图表绘制出错: {e}")
            st.caption("常见原因：选中的列全是空值，或者数值列包含了无法计算的字符。")
