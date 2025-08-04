import { ApolloClient, InMemoryCache } from '@apollo/client';

//const graphqlEndpoint = 'https://api.bookql.com/graphql';

// const graphqlEndpoint = 'https://bookql-api-mcp6.onrender.com/graphql';
const graphqlEndpoint = 'https://www.general-api.com/bookql';

const apolloClient = new ApolloClient({
  uri: graphqlEndpoint,
  cache: new InMemoryCache(),
});

export default apolloClient;