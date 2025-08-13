# import seaborn as sns
# import pandas as pd
# import matplotlib.pyplot as plt
# df = pd.read_csv('2025-07-09.csv')

# sns.barplot(data=df , x = 'status',y='name')
# plt.xticks(rotation = 45)
# plt.show()



import matplotlib.pyplot as plt
import pandas as pd


def make_graph(data='2fa.csv'):
	print('[1] generating graph')
	df = pd.read_csv(data)

	attendance_count = df['name'].value_counts()
	print(attendance_count)
	attendance_count.plot(kind='bar', color='blue')
	plt.title("Total Days Present per Person")
	plt.ylabel("Days Present")
	plt.xlabel("Name")
	plt.xticks(rotation=45)
	plt.tight_layout()
	plt.savefig("plot.png")
	return 1
