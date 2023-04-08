import plotly.express as px
import pandas as pd
import plotly.io
from pandasql import sqldf
#plotly.io.renderers.default = 'chromium'

class PAStarData:
    def __init__(self, database_path):
        self.file_name: str = ''
        self.threads: int = 0
        self.samples_per_size: int = 0
        self.sequences_per_execution: int = 0
        self.max_size: int = 0
        self.database = None

        self.file_name = database_path.split('/').pop()
        file_dict = self.get_dict_from_file_name()

        self.threads = int(file_dict['threads'])
        self.samples_per_size = int(file_dict['SizeSample'])
        self.sequences_per_execution = int(file_dict['Seq'])
        self.max_size = int(file_dict['MaxSize'].replace(".0", ''))

        self.database = pd.read_feather(database_path)
        self.insert_threading_info_into_database()
        self.insert_ratio_info()
        self.convert_time_info()

    def get_dict_from_file_name(self):
        file_tuple_list = list(map(lambda x: tuple(x.split("_")), self.file_name[0:-8].split('-')))
        file_dict = dict(filter(lambda x: True if len(x) == 2 else False, file_tuple_list))

        return file_dict

    def insert_threading_info_into_database(self):
        if self.threads > 1:
            self.database['threading'] = f'multi({self.threads})'
        else:
            self.database['threading'] = 'single'

    def insert_ratio_info(self):
        self.database['Ratio'] = self.database.Nodes/(self.database.Seq_size**self.database.Seq_qtd)*100

    def convert_time_info(self):
        self.database['Time'] = pd.to_timedelta(pd.to_datetime(self.database['Execution_time'],format= '%M:%S.%fs' ).dt.time.astype(str)).dt.total_seconds()

    def get_description(self):
        return f'Sequences: {self.sequences_per_execution}\tSamples per size step: {self.samples_per_size}'

class PAStarDataCollection:

    def __init__(self, databases_array: [PAStarData]):
        self.pastar_data: [PAStarData] = []
        for data in databases_array:
            self.pastar_data.append(data)
        
        print(len(self.pastar_data))

    def add_pastar_data(self, pastar_data):
        self.pastar_data.append(pastar_data)

    def get_merged_database(self):
        main_database = self.pastar_data[0].database.copy()

        for data in self.pastar_data:
            main_database = pd.concat([main_database, data.database.copy()], ignore_index=True)
            print(data.database)

        return main_database

    def get_description(self):

        # Sequences and samples
        sequences_exec = set()
        samples_size = set()
        for data in self.pastar_data:
            sequences_exec.add(data.sequences_per_execution)
            samples_size.add(data.samples_per_size)


        return f'Sequences: {"-".join(map(str, sequences_exec))}\tSamples per size step: {"-".join(map(str,samples_size))}'



print(PAStarDataCollection([PAStarData("./data/SeqResults-SeqDatabase-MaxSize_2000.0-Seq_3-SizeSample_20-Step_100-Samples_400-threads_24.feather")]).get_description())

def format_subtitle(subtitle: str):
    if subtitle != None:
        return f'<br><sup>{subtitle}</sup>'
    else:
        return ''

def build_graph(input, x_input, y_input, title=None, legend_title=None, x_title=None, y_title=None, color=None, file_name: str='file_name', graph_type='scatter', annotation_column_reference='Nodes', show_similarity=False):
    fig = None

    # Build the right graph type
    match graph_type:
        case 'box':
            fig = px.box(y=y_input, x=x_input, color=color)
        case 'scatter':
            fig = px.scatter(y=y_input, x=x_input, color=color)
        case _:
            raise Exception('Invalid graph type')

    # Adding the correct labels to the xaxis
    fig.update_layout(xaxis={"tickmode":"array", "tickvals": x_input})

    # Adding text
    fig.update_layout(
        title={
            'text': title + format_subtitle(None),
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

    if show_similarity == True:
        # Showing min max
        max_df = input.loc[input.index[input.groupby('Seq_size', as_index=False).idxmax(numeric_only=True)[annotation_column_reference]]].reset_index()
        min_df = input.loc[input.index[input.groupby('Seq_size', as_index=False).idxmin(numeric_only=True)[annotation_column_reference]]].reset_index()

        #merged_min_max = pd.concat([max_df.copy(), min_df.copy()], ignore_index=True).sort_values(by=['Seq_size'])
        print(max_df)

        for idx in range(len(max_df)): # Assume same size as min

            is_max_higher_similarity = True if float(max_df.loc[idx]["Similarity"].strip("%")) > float(min_df.loc[idx]["Similarity"].strip("%")) else False

            # Add info for each max
            fig.add_annotation(
                x=max_df.loc[idx]['Seq_size'],
                y=max_df.loc[idx][annotation_column_reference],
                ay=-30,
                showarrow=True,
                text=f'{max_df.loc[idx]["Similarity"]}',
                font=dict(color='red' if is_max_higher_similarity == True else 'black')
            )

            # Add info for each min
            fig.add_annotation(
                x=min_df.loc[idx]['Seq_size'],
                y=min_df.loc[idx][annotation_column_reference],
                ay=30,
                showarrow=True,
                text=f'{min_df.loc[idx]["Similarity"]}',
                font=dict(color='red' if is_max_higher_similarity == False else 'black')
            )

    fig.show()
    #fig.write_image(f"./graphs/{file_name}.png", scale=3.0, width=1900, height=1000)

def merge_data_single_multi(single_thread_data, multi_thread_data):
    multi_thread_data['threading'] = 'multi'
    single_thread_data['threading'] = 'single'

    return pd.concat([multi_thread_data, single_thread_data], ignore_index=True)


# This is just the reduce the amount of times I repeat the same function for the same type of graph
def plot_helper(sequence_size, data_single, data_multi):

    merged_info = PAStarDataCollection([data_multi, data_single])
    total_data = merged_info.get_merged_database()

    print(total_data)

    # Scatter
    build_graph(total_data, total_data.Seq_size, total_data.Nodes, f'Relação de nós e tamanho das sequências {format_subtitle(merged_info.get_description())}', 'Threading', 'Tamanho das sequências', 'Nós visitados', color=total_data.threading, graph_type='scatter', file_name=f'Seq_{sequence_size}-Nodes-Scatter')
    build_graph(data_multi.database, data_multi.database.Seq_size, data_multi.database.Nodes, f'Relação de nós e tamanho das sequências {format_subtitle(data_multi.get_description())}', 'Threading', 'Tamanho das sequências', 'Nós visitados', color=data_multi.database.threading, graph_type='scatter', file_name=f'Seq_{sequence_size}-Nodes-Scatter-Multi-Similarity', show_similarity=True)
    build_graph(data_single.database, data_single.database.Seq_size, data_single.database.Nodes, f'Relação de nós e tamanho das sequências {format_subtitle(data_single.get_description())}', 'Threading', 'Tamanho das sequências', 'Nós visitados', color=data_single.database.threading, graph_type='scatter', file_name=f'Seq_{sequence_size}-Nodes-Scatter-Single-Similarity', show_similarity=True)
    build_graph(total_data, total_data.Seq_size, total_data.Ratio, f'Relação de nós e tamanho das sequências {format_subtitle(merged_info.get_description())}', 'Threading', 'Tamanho das sequências', 'Nós visitados / Pior caso (%)', color=total_data.threading, graph_type='scatter', file_name=f'Seq_{sequence_size}-Nodes_WorstCase-Scatter')

    # Box
    build_graph(total_data, total_data.Seq_size, total_data.Nodes, f'Relação de nós e tamanho das sequências {format_subtitle(merged_info.get_description())}', 'Threading', 'Tamanho das sequências', 'Nós visitados', color=total_data.threading, graph_type='box', file_name=f'Seq_{sequence_size}-Nodes-Box')
    build_graph(data_multi.database, data_multi.database.Seq_size, data_multi.database.Nodes, f'Relação de nós e tamanho das sequências {format_subtitle(data_multi.get_description())}', 'Threading', 'Tamanho das sequências', 'Nós visitados', color=data_multi.database.threading, graph_type='box', file_name=f'Seq_{sequence_size}-Nodes-Box-Multi-Similarity', show_similarity=True)
    build_graph(data_single.database, data_single.database.Seq_size, data_single.database.Nodes, f'Relação de nós e tamanho das sequências {format_subtitle(data_single.get_description())}', 'Threading', 'Tamanho das sequências', 'Nós visitados', color=data_single.database.threading, graph_type='box', file_name=f'Seq_{sequence_size}-Nodes-Box-Single-Similarity', show_similarity=True)
    build_graph(total_data, total_data.Seq_size, total_data.Ratio, f'Relação de nós e tamanho das sequências {format_subtitle(merged_info.get_description())}', 'Threading', 'Tamanho das sequências', 'Nós visitados / Pior caso (%)', color=total_data.threading, graph_type='box', file_name=f'Seq_{sequence_size}-Nodes_WorstCase-Box')

    build_graph(total_data, total_data.Seq_size, total_data.Time, f'Relação de tempo e tamanho das sequências {format_subtitle(merged_info.get_description())}', 'Threading', 'Tamanho das sequências', 'Tempo de execução (seg)', color=total_data.threading, graph_type='box', file_name=f'Seq_{sequence_size}-Time-Box')


# Plotting

data = pd.read_feather("./data/4000_samples.feather")

#data_multi = pd.read_feather("./data/SeqResults-SeqDatabase-MaxSize_2000.0-Seq_3-SizeSample_20-Step_100-Samples_400-threads_24.feather")
#data_single = pd.read_feather("./data/SeqResults-SeqDatabase-MaxSize_2000.0-Seq_3-SizeSample_20-Step_100-Samples_400-threads_1.feather")
#
#total_data = merge_data_single_multi(data_single, data_multi)

data_multi = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_2000.0-Seq_3-SizeSample_20-Step_100-Samples_400-threads_24.feather")
data_single = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_2000.0-Seq_3-SizeSample_20-Step_100-Samples_400-threads_1.feather")
plot_helper(3, data_single, data_multi)


# Seq 4

data_multi = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_400.0-Seq_4-SizeSample_35-Step_50-Samples_245-threads_24.feather")
data_single = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_400.0-Seq_4-SizeSample_35-Step_50-Samples_245-threads_1.feather")
plot_helper(4, data_single, data_multi)


# Seq 5

merged_info = PAStarDataCollection([PAStarData("./data/SeqResults-SeqDatabase-MaxSize_350.0-Seq_5-SizeSample_35-Step_50-Samples_210-threads_24.feather")])
data = merged_info.get_merged_database()

build_graph(data, data.Seq_size, data.Nodes, f'Relação de nós e tamanho das sequências {format_subtitle(merged_info.get_description())}', x_title='Tamanho das sequências', y_title='Nós visitados', color=data.threading, graph_type='box', file_name='Seq_5-Nodes-Box', show_similarity=True)
build_graph(data, data.Seq_size, data.Nodes, f'Relação de nós e tamanho das sequências {format_subtitle(merged_info.get_description())}', x_title='Tamanho das sequências', y_title='Nós visitados', color=data.threading, graph_type='scatter', file_name='Seq_5-Nodes-Scatter', show_similarity=True)


