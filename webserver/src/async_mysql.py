import aiomysql


class MySQLClient:
    def __init__(self, loop):
        self.pool = loop.run_until_complete(aiomysql.create_pool(
		host='mysql',
		user='root',
                password='root',
		db='crypto',
                maxsize=50,
		loop=loop))

        self.TABLES = {
            'Arb': (  # add account_id
                'ask_price',
                'bid_price',
                'volume',
                'base_currency',
                'quote_currency',
                'instrument_pair',
                'ask_exchange',
                'bid_exchange',
		'arb',
		'arb_type',
		'profit',
                'timestamp',
#                'hedge_market',  # varchar(64)
#                'wanted_hedge_price',  # decimal
#                'avail_hedge_price',  # decimal
#                'order_send_time',  # bigint
#                'expected_price'  # decimal
#                'hedge_market_code',  # varchar(8)
#                'market_code'  # varchar(8)
#                # wanted_basis
#                # actual_basis
            ),
        }

    def send_queries(self, queries, values):
        pass

    async def get_last_arb_id(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = 'SELECT arb_id FROM Arb ORDER BY timestamp DESC LIMIT 1'
                await cursor.execute(query)
                result = await cursor.fetchone()
                return result

    async def insert_dict(self, table, row):
        names = []
        value_types = []
        values = []
        for k, v in row.items():
            names.append('`' + k + '`')
            values.append(v)
            value_types.append('%s')

        value_types = ','.join(value_types)
        names = ','.join(names)
        query = f'INSERT INTO `{table}` ({names}) VALUES ({value_types})'

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, values)
            await conn.commit()

    async def insert(self, table, values):
        query = f'INSERT INTO `{table}` ('
        _fields = ''
        for f in self.TABLES[table]:
            _fields += '`' + f + '`, '
        _fields = _fields[:-2] + ')'
        query += _fields + ' VALUES ('
        _values = ''
        for v in values:
            _values += '%s, '
        _values = _values[:-2] + ')'
        query += _values

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, values)
            await conn.commit()

    async def read(self, table, num_rows=1):
        _fields = ''
        for f in self.TABLES[table]:
            _fields += f'`{f}`, '
        _fields = _fields[:-2]
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = f'SELECT {_fields} FROM `{table}`'
                cursor.execute(query)
                if num_rows == 'all':
                    result = cursor.fetchall()
                    return result

                for row in range(num_rows):
                    result = cursor.fetchone()
                    return result

    async def close(self):
        await self.pool.wait_closed()