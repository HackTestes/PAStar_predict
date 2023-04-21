import plotly.express as px
import pandas as pd
import plotly.io
import numpy as np
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

        self.database = pd.read_hdf(database_path)
        self.rebuild_index()
        self.insert_threading_info_into_database()
        self.insert_ratio_info()
        self.convert_time_info()

    def get_dict_from_file_name(self):
        file_tuple_list = list(map(lambda x: tuple(x.split("_")), self.file_name[0:-4].split('-')))
        file_dict = dict(filter(lambda x: True if len(x) == 2 else False, file_tuple_list))

        return file_dict

    def insert_threading_info_into_database(self):
        if self.threads > 1:
            self.database['threading'] = f'multi({self.threads})'
        else:
            self.database['threading'] = 'single'

        self.database['threads'] = self.threads

    def rebuild_index(self):
        self.database.index = range(self.database.shape[0])

    def trim(self, end_index):
        self.database = self.database.iloc[:end_index]

    def insert_ratio_info(self):
        self.database['Ratio'] = self.database.Nodes/(self.database.Seq_size**self.database.Seq_qtd)*100

    def convert_time_info(self):
        phase_1_time = pd.to_timedelta(pd.to_datetime(self.database['Heuristic_time'],format= '%M:%S.%fs' ).dt.time.astype(str)).dt.total_seconds()
        phase_2_time = pd.to_timedelta(pd.to_datetime(self.database['Execution_time'],format= '%M:%S.%fs' ).dt.time.astype(str)).dt.total_seconds()
        self.database['Time'] = phase_1_time + phase_2_time
        #self.database['Time'] = pd.to_timedelta(pd.to_datetime(self.database['Execution_time'],format= '%M:%S.%fs' ).dt.time.astype(str)).dt.total_seconds()

    def get_increase_rate(self, col):
        means = self.database.groupby('Seq_size', as_index=False).mean(numeric_only=True)
        rates = [1] # Since the first value has no previous one, consider 1

        # Compare the previous mean to evaluate the increase
        for row_idx in range(1, means.shape[0]):
            rates.append(round( means.iloc[row_idx][col] / means.iloc[row_idx-1][col], 2 ))

        means['IncreaseRate'] = rates
        means['Threading'] = self.database.threading[0]

        return means

    def get_description(self):
        return f'Sequences: {self.sequences_per_execution}\tSamples per size: {self.samples_per_size}'

class PAStarDataCollection:

    def __init__(self, databases_array: [PAStarData]):
        self.pastar_data: [PAStarData] = []
        for data in databases_array:
            self.pastar_data.append(data)

    def add_pastar_data(self, pastar_data):
        self.pastar_data.append(pastar_data)

    def get_merged_database(self):
        main_database = self.pastar_data[0].database.copy()

        for data in self.pastar_data:
            main_database = pd.concat([main_database, data.database.copy()], ignore_index=True)

        return main_database

    def validate_database(self):
        for dataframe in self.pastar_data:
            result = dataframe.database['Misc'] == self.pastar_data[0].database['Misc']

            if len(pd.unique(result)) > 1 or result[0] == False:
                print(dataframe.database.loc[~result.values], self.pastar_data[0].database[~result.values], sep='\n')
                raise Exception('Score doesn\'t match')

    def get_collection_increase_rate(self, col):

        dataframes = []
        for data in self.pastar_data:
            dataframes.append(data.get_increase_rate(col))

        return pd.concat(dataframes, ignore_index=True)

    def get_relative_performance(self, col, who_idx=0):

        dataframes = []
        for data in self.pastar_data:
            dataframe_copy = data.database.copy()
            dataframe_copy['RelativePerf'] = (self.pastar_data[who_idx].database[col] / data.database[col]).round(0).replace([np.inf, -np.inf], 0)

            dataframes.append(dataframe_copy)

        return pd.concat(dataframes, ignore_index=True).sort_values('threads')

    def get_description(self):

        # Sequences and samples
        sequences_exec = set()
        samples_size = set()
        for data in self.pastar_data:
            sequences_exec.add(data.sequences_per_execution)
            samples_size.add(data.samples_per_size)


        return f'Sequences: {"-".join(map(str, sequences_exec))}\tSamples per size: {"-".join(map(str,samples_size))}'


def format_subtitle(subtitle: str):
    if subtitle != None:
        return f'<br><sup>{subtitle}</sup>'
    else:
        return ''

def build_graph(input, x_input, y_input, title='', legend_title=None, x_title=None, y_title=None, color=None, file_name: str='file_name', graph_type='scatter', annotation_column_reference='Nodes', show_similarity=False):
    fig = None

    # Build the right graph type
    match graph_type:
        case 'box':
            fig = px.box(y=y_input, x=x_input, color=color, points=False)
        case 'scatter':
            fig = px.scatter(y=y_input, x=x_input, color=color)
        case 'bar':
            fig = px.bar(input, x=x_input, y=y_input, color=color, text=y_input, barmode='group')
            fig.add_hline(y=1, line_width=1.5, line_dash="solid", line_color="black")
        case 'line':
            fig = px.line(input, x=x_input, y=y_input, color=color, markers=True)
            fig.update_traces(textposition="top right")
        case _:
            raise Exception('Invalid graph type')

    # Adding the correct labels to the xaxis
    fig.update_layout(xaxis={"tickmode":"array", "tickvals": x_input})

    if graph_type != 'bar' and graph_type != 'line':
        # Add vertical line to help visualization
        x_input_unique = list(set(x_input))
        x_input_unique.sort() # Get the correct order after buiding the set with unique values
        x_input_unique.pop() # Eliminate vlines at the final border

        # Get the value necessary to reach the moddle point
        added_value = (x_input_unique[1]- x_input_unique[0])/2
        print(x_input_unique)

        for x in x_input_unique:
            fig.add_vline(x=x+added_value, line_width=1, line_dash="dash", line_color="white")
            print(f'line {x} \t add: {added_value}')

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

def build_line_chart(x_input, y_input ):
    pass

def merge_data_single_multi(single_thread_data, multi_thread_data):
    multi_thread_data['threading'] = 'multi'
    single_thread_data['threading'] = 'single'

    return pd.concat([multi_thread_data, single_thread_data], ignore_index=True)


# This is just the reduce the amount of times I repeat the same function for the same type of graph
def plot_helper(sequence_size, execution_data): #data_single, data_multi):

    merged_info = PAStarDataCollection(execution_data)
    merged_info.validate_database()
    total_data = merged_info.get_merged_database()

    print(total_data)

#    # Scatter
#    build_graph(total_data, total_data.Seq_size, total_data.Nodes, f'Relationship between nodes visited and sequences\' size {format_subtitle(merged_info.get_description())}', 'Threading', 'Sequence size', 'Nodes visited', color=total_data.threading, graph_type='scatter', file_name=f'Seq_{sequence_size}-Nodes-Scatter')
#    build_graph(total_data, total_data.Seq_size, total_data.Ratio, f'Relationship between nodes visited and sequences\' size {format_subtitle(merged_info.get_description())}', 'Threading', 'Sequence size', 'Nodes visited / Worst case (%)', color=total_data.threading, graph_type='scatter', file_name=f'Seq_{sequence_size}-Nodes_WorstCase-Scatter')
#
#    # Box
#    build_graph(total_data, total_data.Seq_size, total_data.Nodes, f'Relationship between nodes visited and sequences\' size {format_subtitle(merged_info.get_description())}', 'Threading', 'Sequence size', 'Nodes visited', color=total_data.threading, graph_type='box', file_name=f'Seq_{sequence_size}-Nodes-Box')
#    build_graph(total_data, total_data.Seq_size, total_data.Ratio, f'Relationship between nodes visited and sequences\' size {format_subtitle(merged_info.get_description())}', 'Threading', 'Sequence size', 'Nodes visited / Worst case (%)', color=total_data.threading, graph_type='box', file_name=f'Seq_{sequence_size}-Nodes_WorstCase-Box')
#
#    # Time graph
#    build_graph(total_data, total_data.Seq_size, total_data.Time, f'Relationship between time and sequences\' size {format_subtitle(merged_info.get_description())}', 'Threading', 'Sequence size', 'Execution time (sec)', color=total_data.threading, graph_type='box', file_name=f'Seq_{sequence_size}-Time-Box')
#
#    # Shows data with similarity information -> it is better to get sperated info on each for visualization
#    for pastar_data in execution_data:
#        # Scatter
#        build_graph(pastar_data.database, pastar_data.database.Seq_size, pastar_data.database.Nodes, f'Relationship between nodes visited and sequences\' size {format_subtitle(pastar_data.get_description())}', 'Threading', 'Sequence size', 'Nodes visited', color=pastar_data.database.threading, graph_type='scatter', file_name=f'Seq_{sequence_size}-Nodes-Scatter-Threads_{pastar_data.threads}-Similarity', show_similarity=True)
#
#        # Box
#        build_graph(pastar_data.database, pastar_data.database.Seq_size, pastar_data.database.Nodes, f'Relationship between nodes visited and sequences\' size {format_subtitle(pastar_data.get_description())}', 'Threading', 'Sequence size', 'Nodes visited', color=pastar_data.database.threading, graph_type='box', file_name=f'Seq_{sequence_size}-Nodes-Box-Threads_{pastar_data.threads}-Similarity', show_similarity=True)



# Plotting

# Seq 3

data_multi = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_3000.0-Seq_3-SizeSample_20-Step_100-Samples_600-threads_24.hdf")
data_multi.trim(400)

data_multi_12 = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_3000.0-Seq_3-SizeSample_20-Step_100-Samples_600-threads_12.hdf")
data_multi_12.trim(400)

data_single = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_3000.0-Seq_3-SizeSample_20-Step_100-Samples_600-threads_1.hdf")
data_single.trim(400)

collection = PAStarDataCollection([data_single, data_multi_12, data_multi])

data_collec = collection.get_collection_increase_rate('Time')
build_graph(data_collec, x_input=data_collec['Seq_size'], y_input=data_collec['IncreaseRate'], color=data_collec['Threading'], graph_type='line')

relative = collection.get_relative_performance('Time').groupby(['Seq_size', 'threading'], as_index=False).mean(numeric_only=True).sort_values('threads')
build_graph(relative, x_input=relative['Seq_size'], y_input=relative['RelativePerf'], color=relative['threading'], graph_type='bar')

plot_helper(3, [data_single, data_multi_12, data_multi])

# Seq 4

data_multi = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_400.0-Seq_4-SizeSample_15-Step_50-Samples_105-threads_24.hdf")
data_multi_12 = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_400.0-Seq_4-SizeSample_15-Step_50-Samples_105-threads_12.hdf")
data_single = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_400.0-Seq_4-SizeSample_15-Step_50-Samples_105-threads_1.hdf")

plot_helper(4, [data_single, data_multi_12, data_multi])

# Seq 5

data_multi = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_200.0-Seq_5-SizeSample_20-Step_50-Samples_80-threads_24.hdf")
data_multi_12 = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_200.0-Seq_5-SizeSample_20-Step_50-Samples_80-threads_12.hdf")
data_single = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_200.0-Seq_5-SizeSample_20-Step_50-Samples_80-threads_1.hdf")

plot_helper(5, [data_single, data_multi_12, data_multi])

# MAxRSS -> THIS IS JUST AN EXPERIMENT

#data_RSS = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_2500.0-Seq_3-SizeSample_1-Step_50-Samples_49-MaxRSS-threads_24-MaxRSS.hdf")
#build_graph(data_RSS.database, data_RSS.database.Seq_size, data_RSS.database.MaxRSS, f'Relationship between RSS and sequences\' size {format_subtitle(data_RSS.get_description())}', 'Threading', 'Sequence size', 'MaxRSS', color=data_RSS.database.threading, graph_type='box', file_name=f'Seq_{3}-MaxRSS-box')
#
#data_RSS = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_5000.0-Seq_3-SizeSample_5-Step_50-Samples_495-MaxRSS-MaxSim-threads_24-MaxRSS-MaxSim.hdf")
#build_graph(data_RSS.database, data_RSS.database.Seq_size, data_RSS.database.MaxRSS, f'Relationship between RSS and sequences\' size (Max Similarity) {format_subtitle(data_RSS.get_description())}', 'Threading', 'Sequence size', 'MaxRSS', color=data_RSS.database.threading, graph_type='box', file_name=f'Seq_{3}-MaxRSS-MaxSim-box')
#
#data_RSS = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_5000.0-Seq_3-SizeSample_5-Step_50-Samples_495-MaxRSS-MaxSim-threads_24-MaxRSS-MaxSim.hdf")
#build_graph(data_RSS.database, data_RSS.database.Seq_size, data_RSS.database.Nodes, f'Relationship between nodes visited and sequences\' size (Max Similarity) {format_subtitle(data_RSS.get_description())}', 'Threading', 'Sequence size', 'Nodes Visited', color=data_RSS.database.threading, graph_type='box', file_name=f'Seq_{3}-Nodes-MaxSim-box')