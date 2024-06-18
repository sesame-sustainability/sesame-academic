# GraphQL Gotchas 💥

## 1. GraphQL Spec Does Not Support Union Scalar Types

At least, I believe this is the cause of one of the errors we've faced: when creating the GraphQL nodes from our metadata, we were seeing an error with respect to options arrays. Some option lists contain numeric values and some contain strings, but GraphQL (via Gatsby's `createNode`) does not infer a union type of e.g. (string | number)[].

GraphQL does not infer a union type here, and attempting to write the types manually repeatedly led to dead ends. There may be a possible workaround that doesn't involve casting the options to strings, but much time was spent spelunking through both Gatsby and GraphQL docs to no avail.

Ultimately, casting all options to strings was the easiest solution in this case, and makes sense when you consider that all options are passed into `<input>`s, which casts them to strings anyways (when we get the values out of the input, we parse them as floats/ints as needed before sending them to the back-end when performing an analysis).

```js
const mapUserInputs = (u) => ({
  ...u,
  options: u.options
    ? u.options.map(({ value, conditionals }) => ({
        // toString() all options (string | number)...
        // since the GraphQL spec does not support union scalar types:
        // https://github.com/graphql/graphql-spec/issues/215
        value: value.toString(),
        conditionals: mapConditionals(conditionals),
      }))
    : undefined,
});
```

## 2. Empty Arrays Filtered Out

When updating a type in the metadata which is shared across multiple metadata endpoints (e.g. `user_inputs`), it is tempting to add the new field to the query wherever it may appear in the future.

For example, if `user_input`s now have a `foo` property in the pathway metadata, which may return an array of `bar`s, we might update the `Metadata` query in `useAppMetadata` such that all `user_inputs` now query `foo`, even though `foo` only returns data for stages at the moment:

```graphql
query Metadata {
  allStage {
    edges {
      node {
        activities {
          sources {
            id
            name
            user_inputs {
              categorical
              foo {
                bar
              }
            }
          }
        }
      }
    }
  }
  allAnalysis {
    nodes {
      analysis {
        user_inputs {
          categorical
          foo {
            bar
          }
        }
      }
    }
  }
  allSystem {
    nodes {
      system {
        user_inputs {
          categorical
          foo {
            bar
          }
        }
      }
    }
  }
  fleet {
    fleet {
      user_inputs {
        categorical
        foo {
          bar
        }
      }
    }
  }
}
```

However, if the metadata for an endpoint like `fleet` returns an empty array for all instances of `foo`, we cannot query `foo` in the fleet portion of our GraphQL query. This will throw an error at build time along the lines of `Cannot query field "foo" on type "fleetUser_inputs"` -- it seems the empty arrays are filtered out.
