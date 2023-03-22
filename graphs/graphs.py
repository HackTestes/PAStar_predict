import plotly.express as px
import pandas as pd
import plotly.io
#plotly.io.renderers.default = 'chromium'

def build_graph(input, x_input, y_input, title=None, legend_title=None, x_title=None, y_title=None, color=None, file_name: str='file_name', graph_type='scatter'):
    fig = None

    match graph_type:
        case 'box':
            fig = px.box(y=y_input, x=x_input, color=color)
        case 'scatter':
            fig = px.scatter(y=y_input, x=x_input, color=color)
        case _:
            raise Exception('Invalid graph type')

    fig.update_layout(xaxis={"tickmode":"array", "tickvals": x_input})

    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        xaxis_title=x_title,
        yaxis_title=y_title,
        legend_title=legend_title,
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="Black"
        )
    )
    fig.show()
    fig.write_image(f"./graphs/{file_name}.png", scale=3.0, width=1100, height=1000)

def merge_data_single_multi(single_thread_data, multi_thread_data):
    multi_thread_data['threading'] = 'multi'
    single_thread_data['threading'] = 'single'

    return pd.concat([multi_thread_data, single_thread_data], ignore_index=True)

data = pd.read_feather("./data/4000_samples.feather")


#fig = px.scatter(y=data.Nodes, x=data.Seq_size)
#
#fig.update_layout(xaxis={"tickmode":"array", "tickvals": data.Seq_size})
#
#fig.update_layout(
#    title={
#        'text': "Relação de nós e tamanho das sequências",
#        'x': 0.5,
#        'xanchor': 'center',
#        'yanchor': 'top'},
#    xaxis_title="Tamanho das sequências",
#    yaxis_title="Nós",
#    font=dict(
#        family="Courier New, monospace",
#        size=18,
#        color="Black"
#    )
#)
#
##fig.show()
#fig.write_image("./graphs/Nos.png", scale=3.0, width=1100, height=1000)
#
#
#fig = px.scatter(y=(data.Nodes/(data.Seq_size**3))*100, x=data.Seq_size)
#
#fig.update_layout(xaxis={"tickmode":"array", "tickvals": data.Seq_size})
#
#fig.update_layout(
#    title={
#        'text': "Relação de nós e tamanho das sequências",
#        'x': 0.5,
#        'xanchor': 'center',
#        'yanchor': 'top'},
#    xaxis_title="Tamanho das sequências",
#    yaxis_title="Nós / Pior caso",
#    font=dict(
#        family="Courier New, monospace",
#        size=18,
#        color="Black"
#    )
#)
#fig.write_image("./graphs/Nos_PiorCaso.png", scale=3.0, width=1100, height=1000)
#
#

data_multi = pd.read_feather("./data/SeqResults-SeqDatabase-MaxSize_2000.0-Seq_3-SizeSample_20-Step_100-Samples_400-threads_24.feather")
data_single = pd.read_feather("./data/SeqResults-SeqDatabase-MaxSize_2000.0-Seq_3-SizeSample_20-Step_100-Samples_400-threads_1.feather")

total_data = merge_data_single_multi(data_single, data_multi)

print(total_data)

# Seq 3

build_graph(total_data, total_data.Seq_size, total_data.Nodes, 'Relação de nós e tamanho das sequências (3)', 'Threading', 'Tamanho das sequências', 'Nós visitados', color=total_data.threading, graph_type='scatter', file_name='Seq_3-Nodes-Scatter')
build_graph(total_data, total_data.Seq_size, total_data.Nodes/(total_data.Seq_size**total_data.Seq_qtd)*100, 'Relação de nós e tamanho das sequências (3)', 'Threading', 'Tamanho das sequências', 'Nós visitados / Pior caso (%)', color=total_data.threading, graph_type='scatter', file_name='Seq_3-Nodes_WorstCase-Scatter')

build_graph(total_data, total_data.Seq_size, total_data.Nodes, 'Relação de nós e tamanho das sequências (3)', 'Threading', 'Tamanho das sequências', 'Nós visitados', color=total_data.threading, graph_type='box', file_name='Seq_3-Nodes-Box')
build_graph(total_data, total_data.Seq_size, total_data.Nodes/(total_data.Seq_size**total_data.Seq_qtd)*100, 'Relação de nós e tamanho das sequências (3)', 'Threading', 'Tamanho das sequências', 'Nós visitados / Pior caso (%)', color=total_data.threading, graph_type='box', file_name='Seq_3-Nodes_WorstCase-Box')

# Seq 4

data_multi = pd.read_feather("./data/SeqResults-SeqDatabase-MaxSize_500.0-Seq_4-SizeSample_40-Step_50-Samples_400-threads_24.feather")
data_single = pd.read_feather("./data/SeqResults-SeqDatabase-MaxSize_500.0-Seq_4-SizeSample_40-Step_50-Samples_400-threads_1.feather")

total_data = merge_data_single_multi(data_single, data_multi)

print(total_data)
build_graph(total_data, total_data.Seq_size, total_data.Nodes, 'Relação de nós e tamanho das sequências (4)', 'Threading', x_title='Tamanho das sequências', y_title='Nós visitados', color=total_data.threading, graph_type='box', file_name='Seq_4-Nodes-Box')
build_graph(total_data, total_data.Seq_size, total_data.Nodes, 'Relação de nós e tamanho das sequências (4)', 'Threading', x_title='Tamanho das sequências', y_title='Nós visitados', color=total_data.threading, graph_type='scatter', file_name='Seq_4-Nodes-Scatter')

build_graph(total_data, total_data.Seq_size, total_data.Nodes/(total_data.Seq_size**total_data.Seq_qtd)*100, 'Relação de nós e tamanho das sequências (4)', 'Threading', x_title='Tamanho das sequências', y_title='Nós visitados / Pior caso (%)', color=total_data.threading, graph_type='box', file_name='Seq_4-Nodes_WorstCase-Box')
build_graph(total_data, total_data.Seq_size, total_data.Nodes/(total_data.Seq_size**total_data.Seq_qtd)*100, 'Relação de nós e tamanho das sequências (4)', 'Threading', x_title='Tamanho das sequências', y_title='Nós visitados / Pior caso (%)', color=total_data.threading, graph_type='scatter', file_name='Seq_4-Nodes_WorstCase-Scatter')


# Seq 5

data = pd.read_feather("./data/SeqResults-SeqDatabase-MaxSize_500.0-Seq_5-SizeSample_40-Step_50-Samples_400-threads_24.feather")
build_graph(data, data.Seq_size, data.Nodes, 'Relação de nós e tamanho das sequências (5)', x_title='Tamanho das sequências', y_title='Nós visitados', graph_type='box', file_name='Seq_5-Nodes-Box')
build_graph(data, data.Seq_size, data.Nodes, 'Relação de nós e tamanho das sequências (5)', x_title='Tamanho das sequências', y_title='Nós visitados', graph_type='scatter', file_name='Seq_5-Nodes-Scatter')
