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
        #self.convert_MaxRSS_KiB_to_bytes()

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

    # Get onlt part of the data
    def trim(self, end_index):
        self.database = self.database.iloc[:end_index]

    def insert_ratio_info(self):
        self.database['Ratio'] = self.database.Nodes/(self.database.Seq_size**self.database.Seq_qtd)*100

    def convert_time_info(self):
        phase_1_time = pd.to_timedelta(pd.to_datetime(self.database['Heuristic_time'],format= '%M:%S.%fs' ).dt.time.astype(str)).dt.total_seconds()
        phase_2_time = pd.to_timedelta(pd.to_datetime(self.database['Execution_time'],format= '%M:%S.%fs' ).dt.time.astype(str)).dt.total_seconds()
        self.database['Time'] = (phase_1_time + phase_2_time).replace(0.0, 0.001) # I am rounding the time when it is equal to zero (this means it was really fast!)

        # Sanity check
        if self.database['Time'].isin([0]).any():
            raise Exception('There is a zero value in time')

    def convert_MaxRSS_KiB_to_bytes(self):
        self.database.MaxRSS = self.database.MaxRSS * 1024

    def get_increase_rate(self, col):
        means = self.database.groupby('Seq_size', as_index=False).mean(numeric_only=True)


        #rates = [1] # Since the first value has no previous one, consider 1
        ## Compare the previous mean to evaluate the increase
        #for row_idx in range(1, means.shape[0]):
        #    rates.append(round( means.iloc[row_idx][col] / means.iloc[row_idx-1][col], 2 ))

        # Get the increase rate in relation to the first item
        rates = (means[col] / means.iloc[1][col]).round(2)

        means['IncreaseRate'] = rates
        means['Threading'] = self.database.threading[0]

        return means

    def get_means(self):
        means = means = self.database.groupby('Seq_size', as_index=False).mean(numeric_only=True)
        means['threading'] = self.database.threading[0]
        means['threads'] = self.threads

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
            result = dataframe.database['G_score'] == self.pastar_data[0].database['G_score']

            if len(pd.unique(result)) > 1 or result[0] == False:
                print(dataframe.database.loc[~result.values], self.pastar_data[0].database[~result.values], sep='\n')
                raise Exception('Score doesn\'t match')

    def get_collection_increase_rate(self, col):

        dataframes = []
        for data in self.pastar_data:
            dataframes.append(data.get_increase_rate(col))

        return pd.concat(dataframes, ignore_index=True)

    def get_relative_performance(self, col, who_idx=0, reference_col_as_denominator=False):

        dataframes = []
        for data in self.pastar_data:
            dataframe_copy = data.database.copy()

            if reference_col_as_denominator == False:
                dataframe_copy['RelativePerf'] = (self.pastar_data[who_idx].database[col] / data.database[col]).round(2)

            else:
                dataframe_copy['RelativePerf'] = (data.database[col] / self.pastar_data[who_idx].database[col]).round(2)

            dataframes.append(dataframe_copy)

        return pd.concat(dataframes, ignore_index=True).sort_values('threads')

    def get_collection_means(self):
        dataframes = []

        for data in self.pastar_data:
            dataframes.append(data.get_means().copy())

        return pd.concat(dataframes, ignore_index=True).sort_values(['threads', 'Seq_size'])

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
            return
            fig = px.box(y=y_input, x=x_input, color=color, points=False)
        case 'scatter':
            return
            fig = px.scatter(y=y_input, x=x_input, color=color)
        case 'bar':
            return
            fig = px.bar(input, x=x_input, y=y_input, color=color, barmode='group', pattern_shape=color)
            fig.add_hline(y=1, line_width=1.5, line_dash="solid", line_color="black")

            # Remove annoying bars when they are mostly the same (this just lowers them)
            fig.update_yaxes(range=[min(y_input-0.3), max(y_input+1)])
            #fig.update_layout( yaxis = dict(tickmode = 'linear', tick0 = 0, dtick = 1) )
        case 'line':
            fig = px.line(input, x=x_input, y=y_input, color=color, markers=True, line_dash=color, symbol=color)
            #fig.add_hline(y=1, line_width=1.5, line_dash="solid", line_color="black")
            fig.update_traces(textposition="top right")
        case _:
            raise Exception('Invalid graph type')

    # Adding the correct labels to the xaxis
    fig.update_layout(xaxis={"tickmode":"array", "tickvals": x_input})

    # White backgroud color
    fig.update_layout(plot_bgcolor="#FFFFFF")

    # Line customization for black and white print
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black', gridcolor='#FFFFFF')
    fig.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor='#AAAAAA')


    if graph_type != 'bar' and graph_type != 'line':
        # Add vertical line to help visualization
        x_input_unique = list(set(x_input))
        x_input_unique.sort() # Get the correct order after buiding the set with unique values
        x_input_unique.pop() # Eliminate vlines at the final border

        # Get the value necessary to reach the moddle point
        added_value = (x_input_unique[1]- x_input_unique[0])/2

        for x in x_input_unique:
            fig.add_vline(x=x+added_value, line_width=1, line_dash="dash", line_color="grey")

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

    # Check if the info is valid
    merged_info.validate_database()
    total_data = merged_info.get_merged_database()
    total_data_averages = merged_info.get_collection_means()

    print(total_data, total_data_averages, sep='\n\n')

#    # Scatter
#    build_graph(total_data, total_data.Seq_size, total_data.Nodes, f'Relationship between nodes visited and sequences\' size {format_subtitle(merged_info.get_description())}', 'Threading', 'Sequence size', 'Nodes visited', color=total_data.threading, graph_type='scatter', file_name=f'Seq_{sequence_size}-Nodes-Scatter')
#    build_graph(total_data, total_data.Seq_size, total_data.Ratio, f'Relationship between nodes visited and sequences\' size {format_subtitle(merged_info.get_description())}', 'Threading', 'Sequence size', 'Nodes visited / Worst case (%)', color=total_data.threading, graph_type='scatter', file_name=f'Seq_{sequence_size}-Nodes_WorstCase-Scatter')
#
    # Box
    build_graph(total_data, total_data.Seq_size, total_data.Nodes, f'Relationship between nodes visited and sequences\' size {format_subtitle(merged_info.get_description())}', None, 'Sequence size', 'Nodes visited', color=total_data.threading, graph_type='box', file_name=f'Seq_{sequence_size}-Nodes-Box')
    build_graph(total_data, total_data.Seq_size, total_data.Ratio, f'Relationship between nodes visited and sequences\' size {format_subtitle(merged_info.get_description())}', None, 'Sequence size', 'Nodes visited / Worst case (%)', color=total_data.threading, graph_type='box', file_name=f'Seq_{sequence_size}-Nodes_WorstCase-Box')
    build_graph(total_data, total_data.Seq_size, total_data.MaxRSS, f'Relationship between MaxRSS and sequences\' size {format_subtitle(merged_info.get_description())}', None, 'Sequence size', 'MaxRSS (KiB)', color=total_data.threading, graph_type='box', file_name=f'Seq_{sequence_size}-MaxRSS-Box')

    # Line
    build_graph(total_data_averages, total_data_averages.Seq_size, total_data_averages.Nodes, f'Relationship between nodes visited and sequences\' size {format_subtitle(merged_info.get_description())}', None, 'Sequence size', 'Nodes visited', color=total_data_averages.threading, graph_type='line', file_name=f'Seq_{sequence_size}-Nodes-Line')
    build_graph(total_data_averages, total_data_averages.Seq_size, total_data_averages.MaxRSS, f'Relationship between MaxRSS and sequences\' size {format_subtitle(merged_info.get_description())}', None, 'Sequence size', 'MaxRSS (KiB)', color=total_data_averages.threading, graph_type='line', file_name=f'Seq_{sequence_size}-MaxRSS-Line')
    build_graph(total_data_averages, total_data_averages.Seq_size, total_data_averages.Time, f'Relationship between time and sequences\' size {format_subtitle(merged_info.get_description())}', None, 'Sequence size', 'Execution time (sec)', color=total_data_averages.threading, graph_type='line', file_name=f'Seq_{sequence_size}-Time-Line')

    # Time graph
    build_graph(total_data, total_data.Seq_size, total_data.Time, f'Relationship between time and sequences\' size {format_subtitle(merged_info.get_description())}', None, 'Sequence size', 'Execution time (sec)', color=total_data.threading, graph_type='box', file_name=f'Seq_{sequence_size}-Time-Box')

    # Relative performance
    # Speedup
    relative = merged_info.get_relative_performance('Time').groupby(['Seq_size', 'threading'], as_index=False).mean(numeric_only=True)
    relative = relative.sort_values('threads') # This is just to get the correct colors in the graph

    build_graph(relative, x_input=relative['Seq_size'], y_input=relative['RelativePerf'],  title=f'Speedup between diffrent configurations {format_subtitle(merged_info.get_description())}', x_title='Sequence size', y_title='Speedup', color=relative['threading'], graph_type='bar', file_name=F'Seq_{sequence_size}-SpeedupGraph')

    # Relative memory usage
    relative = merged_info.get_relative_performance('MaxRSS', reference_col_as_denominator=True).groupby(['Seq_size', 'threading'], as_index=False).mean(numeric_only=True)
    relative = relative.sort_values('threads') # This is just to get the correct colors in the graph

    build_graph(relative, x_input=relative['Seq_size'], y_input=relative['RelativePerf'],  title=f'Relative memory usage (MaxRSS) between diffrent configurations {format_subtitle(merged_info.get_description())}', x_title='Sequence size', y_title='Relative Memory Usage', color=relative['threading'], graph_type='bar', file_name=F'Seq_{sequence_size}-RelativeMem')


    # Increase rate -> how fast does it grow?
    # Time
    data_collec = merged_info.get_collection_increase_rate('Time')
    build_graph(data_collec, x_input=data_collec['Seq_size'], y_input=data_collec['IncreaseRate'], title=f'Time increase rate {format_subtitle(merged_info.get_description())}', x_title='Sequence size', y_title='Time increase rate', color=data_collec['Threading'], graph_type='line', file_name=f'Seq_{sequence_size}-TimeIncreaseRate')

    data_collec = merged_info.get_collection_increase_rate('MaxRSS')
    build_graph(data_collec, x_input=data_collec['Seq_size'], y_input=data_collec['IncreaseRate'], title=f'Memory increase rate {format_subtitle(merged_info.get_description())}', x_title='Sequence size', y_title='Memory increase rate', color=data_collec['Threading'], graph_type='line', file_name=f'Seq_{sequence_size}-MaxRSSIncreaseRate')


#    # Shows data with similarity information -> it is better to get sperated info on each for visualization
#    for pastar_data in execution_data:
#        # Scatter
#        build_graph(pastar_data.database, pastar_data.database.Seq_size, pastar_data.database.Nodes, f'Relationship between nodes visited and sequences\' size {format_subtitle(pastar_data.get_description())}', 'Threading', 'Sequence size', 'Nodes visited', color=pastar_data.database.threading, graph_type='scatter', file_name=f'Seq_{sequence_size}-Nodes-Scatter-Threads_{pastar_data.threads}-Similarity', show_similarity=True)
#
#        # Box
#        build_graph(pastar_data.database, pastar_data.database.Seq_size, pastar_data.database.Nodes, f'Relationship between nodes visited and sequences\' size {format_subtitle(pastar_data.get_description())}', 'Threading', 'Sequence size', 'Nodes visited', color=pastar_data.database.threading, graph_type='box', file_name=f'Seq_{sequence_size}-Nodes-Box-Threads_{pastar_data.threads}-Similarity', show_similarity=True)



# Plotting

# Seq 3

data_single = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_2000-Seq_3-SizeSample_5-Step_100-Samples_100-threads_1.hdf")
data_multi_8 = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_2000-Seq_3-SizeSample_5-Step_100-Samples_100-threads_8.hdf")
data_multi_12 = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_2000-Seq_3-SizeSample_5-Step_100-Samples_100-threads_12.hdf")
data_multi_16 = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_2000-Seq_3-SizeSample_5-Step_100-Samples_100-threads_16.hdf")
data_multi_24 = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_2000-Seq_3-SizeSample_5-Step_100-Samples_100-threads_24.hdf")

plot_helper(3, [data_single, data_multi_8, data_multi_12, data_multi_16, data_multi_24])


# Seq 4

data_single = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_500-Seq_4-SizeSample_5-Step_50-Samples_50-threads_1.hdf")
data_multi_8 = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_500-Seq_4-SizeSample_5-Step_50-Samples_50-threads_8.hdf")
data_multi_12 = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_500-Seq_4-SizeSample_5-Step_50-Samples_50-threads_12.hdf")
data_multi_16 = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_500-Seq_4-SizeSample_5-Step_50-Samples_50-threads_16.hdf")
data_multi_24 = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_500-Seq_4-SizeSample_5-Step_50-Samples_50-threads_24.hdf")

plot_helper(4, [data_single, data_multi_8, data_multi_12, data_multi_16, data_multi_24])


# Seq 5

data_single = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_200-Seq_5-SizeSample_5-Step_50-Samples_20-threads_1.hdf")
data_multi_8 = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_200-Seq_5-SizeSample_5-Step_50-Samples_20-threads_8.hdf")
data_multi_12 = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_200-Seq_5-SizeSample_5-Step_50-Samples_20-threads_12.hdf")
data_multi_16 = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_200-Seq_5-SizeSample_5-Step_50-Samples_20-threads_16.hdf")
data_multi_24 = PAStarData("./data/SeqResults-SeqDatabase-MaxSize_200-Seq_5-SizeSample_5-Step_50-Samples_20-threads_24.hdf")

plot_helper(5, [data_single, data_multi_8, data_multi_12, data_multi_16, data_multi_24])