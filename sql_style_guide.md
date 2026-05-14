# Code Style. Ejemplos correctos e incorrectos. 
# *Introduction*

Writing SQL code that materializes dbt data models is an **iterative** and **collaborative** practice. The results of following a style guide are:

- Easily read and maintained SQL code
- An efficient code review and QA process
- Easily identified patterns in our code base in order to adhere to DRY (don’t repeat yourself) principles

## *General Principles*

- It is our collective responsibility to follow and enforce this style guide. The expectation is that our team will use the style presented in this guide during code development and code review, and especially for any code files committed to the Analytics Github code repository
- Our goal is to optimize primarily for readability, maintainability, and robustness rather than for fewer lines of code. Additional lines of code are cheap, time is expensive
## *High Level Style Guide Rules*

- Import CTEs as demonstrated by dbt --> [here](https://docs.getdbt.com/best-practices/how-we-structure/4-marts?version=1.12#marts-models) are not preferred. To improve code density and clarity of source use the `{{ ref() }}` function directly within the body of your SQL:

```sql
select 
    c.customer_name, 
    o.order_date
from {{ ref('stg_crm__customers') }} as c
join {{ ref('stg_crm__orders') }} as o
  on c.customer_id = o.customer_id
```

Here's a non-trivial test query to give you an idea of what this style guide looks like in the practice:

```sql
with decisions as (
  select
    -- first column should always be the primary key
    rpt.sf_decision_id as decision_id, 
    --the timestamps are suffixed with `_at`
    rpt.date_of_decision_c::timestamp as decision_created_at, 
    -- the dates are suffixed with `_date`
    rpt.date_of_decision_c::date as decision_date, 
    -- for case statements, separate the when statements for readability
    case
    	when rpt.decision_type = 'abc' then 1
		when rpt.decision_type = 'def' then 2
		else 0
    end as decision_enum
    
  -- Use recognizable aliases. This helps with debugging/reviewing the code
  from rpt_decision_history as rpt 
  left join stgsn_submission_c as sub
    --the column to be joined will come on the right side
    on rpt.submission_id = sub.id 
  where 1 = 1 --helps when other clauses need to be commented out for testing
    --Multiple where clauses should be on separate lines
    and rpt.date_of_decision_c::date >= '2022-01-01' 
    and sub.iso_competing_sub_c is null
),

decision_sample as ( --Use descriptive CTE names
  select 
    1 as decision_id, 
    csv.created as decision_created_at,
    csv.created::date as decision_date 
  from decisions_csv as csv 
),

combined_decisions as (
  select * from decisions
  union all --Make use of Union All instead of Union to avoid filtering out rows
  select * from decisions_sample
),
    
final as (
  select
    d.decision_id,
    coalesce(b.decision_date, d.decision_date) as decision_date,
    --Boolean fields should be prefixed with `was_`, `is_`, `has_`, or `does_`. For example, `is_customer`, `has_unsubscribed`, etc.
    iff(ad.decision_type = 'Decline', 1, 0))::boolean as is_declined,
	row_number() over (partition by d.decision_id order by decision_date desc) as instance
  from combined_decisions as d
  --Be intentional with inner vs left joins
  inne join advances as ad 
    on d.full_name = ad.full_name
    and d.decision_date = d.decision_date
  group by 1,2
  <!-- Use qualify to dedupe rows instead of creating extra CTE -->
  qualify instance = 1
)

select * from final
```

## *Code Formatting*

### Use lowercase SQL
It's just as readable as uppercase SQL and you won't have to constantly be holding down a shift key.

### Single line vs multiple line queries

The only time to put all of your SQL on one line is when you're selecting:

* All columns (*) or selecting a few columns (~ <5)
* _And_ there's no additional complexity in your query

The reason for this is simply that it's still easy to read this when everything is on one line. But once you start adding more columns or more complexity, it's easier to read if it's on multiple lines.

Use trailing commas (as opposed to leading commas)
Commas should be followed by a space before the column name and the first column name should be aligned for readability:

```sql
-- Bad (too many columns on one line)
select id, email, created_at, is_customer, is_unsubscribed
from users

-- Bad (id should be on a new line as well)
select id,
    email
from users

-- Good
select
  id,
  email,
  created_at
from users

-- Good
select *
from users
where email = 'example@domain.com'
```

For queries that have 1 or 2 columns, you can place the columns on the same line. For >4 columns, _place each column name on its own line_, including the first item.

### Left align all command words

- When `select`-ing, use a single tab to indent
	- Align `from`, `join`, `where`, and `group by` calls with the `select` indentation (i.e. one tab from the left edge)
- When there are multiple conditions for a `join` or multiple `where` conditions give each condition its own row and indent by one tab

```sql
-- Good
select id, email
from users
where email like '%@gmail.com'

-- Good
select id, email
from users
where 1=1
  and email like '%@gmail.com'
  and state = 'CA'

-- Bad
select id, email
  from users
 where email like '%@gmail.com'

 -- Bad
select id, email
from users
where 1=1
and email like '%@gmail.com'
and state = 'CA'
```

### Use single quotes

Some SQL dialects like BigQuery support using double quotes, but for most dialects double quotes will wind up referring to column names. For that reason, single quotes are preferable:

```sql
-- Good
select *
from users
where email = 'example@domain.com'

-- Bad
select *
from users
where email = "example@domain.com"
```

### Use `!=` over `<>`

Simply because `!=` reads like "not equal" which is closer to how we'd say it out loud.

```sql
-- Good
select count(user_id) as paying_users_count
from users
where plan_name != 'free'
```

### Indenting where conditions

When there's only one where condition, leave it on the same line as `where`:

```sql
select email
from users
where id = 1234
```

When there are multiple, indent each condition one level deeper than the `where`. Use 'where 1=1' to make condition testing straight-forward. Put logical operators at the beginning of the condition:

```sql
select id, email
from users
where 1=1
    and created_at >= '2019-03-01'
    and vertical = 'work'
```

### Avoid spaces inside of parenthesis

```sql
-- Good
select *
from users
where id in (1, 2)

-- Bad
select *
from users
where id in ( 1, 2 )
```

### Use spaces after commas and before and after operators

```sql
-- Good
select
  u.id,
  u.first_name || ' ' || u.last_name as full_name,
  coalesce(u.count_orders, 0) as count_orders,
  u.count_orders + u.count_returns as net_orders
from users

-- Bad
select
  u.id,
  u.first_name||' '||u.last_name as full_name,
  coalesce(u.count_orders,0) as count_orders,
  u.count_orders+u.count_returns as net_orders
from users
```

### Break long lists of `in` values into multiple indented lines

```sql
-- Good
select *
from users
where email in (
  'user-1@example.com',
  'user-2@example.com',
  'user-3@example.com',
  'user-4@example.com'
)
```
### Column order conventions

Put the primary key first, followed by foreign keys, then by timestamps (`created_at`, `updated_at`,`bound_at`,`cancellation_at`). If the table has any boolean flags (`is_latest`, `is_initial`, etc.), put those last.

```sql
-- Good
select
  customer_id,
  order_id,
  campaign_id,
  number_of_orders,
  is_new_customer,
  created_at
from customers

-- Bad
select
  created_at,
  order_id,
  number_of_orders,
  campaign_id,
  is_new_customer,
  customer_id
from customers
```

## *Naming Conventions*

### Table names should be descriptive and a plural snake case of the noun

```sql
-- Good
select * from new_submissions
select * from decisions

-- Bad
select * from n_subs
select * from decision_t
```

### Column names should be snake_case

```sql
-- Good
select
  id,
  email,
  timestamp_trunc(created_at, month) as bound_month
from users

-- Bad
select
  id,
  email as CustEmail,
  timestamp_trunc(created_at, month) as BoundMonth
from users
```
### Column name conventions

* Boolean fields should be prefixed with `was_`, `is_`, `has_`, or `does_`. For example, `is_customer`, `has_unsubscribed`, etc.
* aggregation fields should be prefixed with `count_`, `sum_`, or `max_`. For example, `count_policy_vehicles`, `max_policy_driver_age`, etc.
* Date-only fields should be suffixed with `_date`. For example, `cancellation_date`.
* Date-part fields should be suffixed with `_{date_part}`. For example, `cancellation_month`.
* Date+time fields should be suffixed with `_at`. For example, `created_at`, `cancellation_at`, etc.
* Primary or Surrogate columns should be suffixed with `_key` when being created as a surrogate key.
* Alias `id` columns in the staging layer as `[table_name]_id` (e.g., `submissions.id` becomes `submission_id`) for clarity, at the developer's discretion
* In staging layer, `uuid` type columns should be re-aliased, prefixed with the name of the table.
* In the staging layer, the `__c` suffix should be removed from Salesforce columns.

### Always include either table names or table aliases

By doing it this way when we inevitably have to make changes to the table, joining a table with shared column names won't be problematic

```sql
-- Good
select
  c.id,
  c.name
from companies as c

-- Bad
select
  id,
  name
from companies
```

### Always rename aggregates and function-wrapped arguments

```sql
-- Good
select count(u.user_id) as total_users
from users as u

-- Bad
select count(user_id)
from users as u

-- Good
select timestamp_millis(contact.property_beacon_interest) as expressed_interest_at
from hubspot.contact
where contact.property_beacon_interest is not null

-- Bad
select timestamp_millis(contact.property_beacon_interest)
from hubspot.contact
where contact.property_beacon_interest is not null
```

### Use `as` to alias column _and_ table names

```sql
-- Good
select
  u.id,
  u.email,
  u.timestamp_trunc(u.created_at, month) as signup_month
from users as u

-- Bad
select
  u.id,
  u.email,
  u.timestamp_trunc(u.created_at, month) signup_month
from users as u
```


### Take advantage of lateral column aliasing

```sql
-- Good
select
  timestamp_trunc(com_created_at, year) as signup_year,
  count(company_id) as total_companies
from companies
group by signup_year

-- Bad
select
  timestamp_trunc(com_created_at, year) as signup_year,
  count(company_id) as total_companies
from companies
group by timestamp_trunc(com_created_at, year)
```

### Use meaningful CTE names

```sql
-- Good
with ordered_details as (

-- Bad
with d1 as (
```

- In addition, table and column names should be **descriptive** of what is represented in them
- The `as` keyword should be used when aliasing a column or expression
	- Exception for tables; you should alias tables with single letters starting with `a`
- Always alias grouping aggregates and other column expressions

## *Code Conventions*

### Be explicit in boolean conditions

```sql
-- Good
select * from customers where is_cancelled = true
select * from customers where is_cancelled = false

-- Bad
select * from customers where is_cancelled
select * from customers where not is_cancelled
```

### Group by either column name _or_ ordinal position.

```sql
-- Good
select user_id, count(charge_id) as total_charges
from charges
group by user_id

-- Good
select
  user_id,
  count(charge_id) as total_charges
from charges
group by 1

-- Bad
select
  user_id,
  product_id,
  count(charge_id) as total_charges
from charges
group by 1, product_id
```
### Grouping columns should go first

```sql
-- Good
select
  timestamp_trunc(com_created_at, year) as signup_year,
  count(company_id) as total_companies
from companies
group by signup_year

-- Bad
select
  count(company_id) as total_companies,
  timestamp_trunc(com_created_at, year) as signup_year
from mysql_helpscout.helpscout_companies
group by signup_year
```

### Aligning case/when statements

Each `when` should be on its own line (nothing on the `case` line) and should be indented one level deeper than the `case` line. The `then` can be on the same line or on its own line below it, just aim to be consistent.

```sql
-- ideal
select
  case
      when e.event_name = 'viewed_homepage' then 'homepage'
      when e.event_name = 'viewed_editor' then 'editor'
  end as page_name
from events as e

-- Fine-ish
select
    case
      when e.event_name = 'viewed_homepage'
          then 'homepage'
      when e.event_name = 'viewed_editor'
          then 'editor'
  end as page_name
from events as e

-- Bad
select
  case when event_name = 'viewed_homepage' then 'Homepage'
      when event_name = 'viewed_editor' then 'Editor'
  end as page_name
from events
```

### Use CTEs, not subqueries

Avoid subqueries; CTEs will make your queries easier to read and reason about.

If you use any CTEs, always have a CTE named `final` and `select * from final` at the end. That way you can quickly inspect the output of other CTEs used in the query to debug the results.

Closing CTE parentheses should use the same indentation level as `with` and the CTE names.

```sql
-- Good
with ordered_details as (
    select
      bsd.user_id,
      bsd.name,
      row_number() over (partition by bsd.user_id order by bsd.date_updated desc) as details_rank
    from billingdaddy.billing_stored_details as bsd
),

final as (
    select user_id, name
    from ordered_details
    where details_rank = 1
)

select * from final

-- Bad
select user_id, name
from (
    select
      bsd.user_id,
      bsd.name,
      row_number() over (partition by bsd.user_id order by bsd.date_updated desc) as details_rank
    from billingdaddy.billing_stored_details as bsd
) ranked
where details_rank = 1
```

### Window functions

- You can leave it all on its own line or break it up into multiple depending on its length.
- Use `qualify()` function to dedupe or rank on partitions:

```sql
-- Ideal
select
  bsd.user_id,
  bsd.name    
from billingdaddy.billing_stored_details as bsd
qualify row_number() over (partition by bsd.user_id order by bsd.date_updated desc) = 1

-- Fine-ish
with _rank as (
select
  bsd.user_id,
  bsd.name,
  row_number() over (partition by bsd.user_id order by bsd.date_updated desc) as instance
from billingdaddy.billing_stored_details as bsd
)
select * 
from _rank
where instance = 1
```

- Prefer `union all` to `union` and `full outer join`
	- This is because a `union` could indicate an upstream data integrity issue which could be better solved in an upstream data model
- Avoid using an `order by` clause within your data models unless it's necessary to produce the correct result
	- There's no need to incur the performance hit; if consumers of the query need the results ordered they can normally do that themselves

## *JOIN Statement Conventions*

### Prefix your column names with the table alias
	- If only selecting from one table, prefixes are not needed

### Never use `using` in joins because it produces inaccurate results in Snowflake
### Always be explicit with join types

Specifying 'inner' makes it easier to identify this join type for code review and bug fixing:

### Every join condition should be on a new indented line after the join

```sql
-- Good
select
  email,
  sum(amount) as total_revenue
from users
inner join charges
  on users.id = charges.user_id
group by 1

-- Bad
select
  email,
  sum(amount) as total_revenue
from users
inner join charges on users.id = charges.user_id
group by 1
```

### Referenced table should come first in join condition
For join conditions, put the table that was referenced first immediately after the `on`. By doing it this way it makes it easier to determine if your join is going to cause the results to fan out:
```sql
-- Good
    -- primary_key = foreign_key --> one-to-many --> fanout
select
    ...
from users
left join charges
  on users.id = charges.user_id
-- Good
    -- foreign_key = primary_key --> many-to-one --> no fanout
select
    ...
from charges
left join users
  on charges.user_id = users.id

-- Bad
select
    ...
from users
left join charges using (id)
```

## *Commenting*
- For newer, more complicated SQL statements we recommend using comments to provide a description of less commonly seen SQL logic for reference to yourself later or for reference for other team members to better understand a given query
- When making comments in a model always use the “/\* \*/” syntax
	<!-- - This allows single-line comments to naturally expand into 
  multi-line comments as needed without having to change their syntax -->
- Respect the character line limit when making comments
	- Move to a new line if the comment is too long
