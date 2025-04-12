def load_data(self, df):
        """
        Load final processed data to MongoDB.
        Converts date to datetime to avoid BSON encoding errors.
        """
        df['date_only'] = pd.to_datetime(df['date_only'])
        mongoclient = MongoClient('mongodb+srv://sufiyan96:bscs2016@cluster0.nnspm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
        db = mongoclient['BDA_Data']
        collection = db['Stock_New']

        records = df.to_dict(orient='records')

        if records:
            collection.insert_many(records)
            print(f"Inserted {len(records)} documents into collection.")
        else:
            print("No records to insert.")