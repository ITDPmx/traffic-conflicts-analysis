export type Activities = {
  taken_at: string;
  counts: Record<string, number>;
};

export type ActivitiesByDay = {
  taken_at: string;
  counts: {
    [key: string]: number;
  };
};
export type ActivityData = {
  date: string;
  count: number;
};
export type ActivityDataByDay = Record<string, ActivityData[]>; // { 'activity': [{date: '2020-01-01', count: 1}, {date: '2020-01-02', count: 2}] }

export function activitiesPerDay(
  activitiesArray: ActivitiesByDay[]
): Record<string, ActivityData[]> {
  // Parse the JSON string into an array of ActivitiesByDay objects

  // Initialize an empty dictionary to hold our results
  let activityDict: Record<string, ActivityData[]> = {};

  // Iterate over the array of activities
  for (const activity of activitiesArray) {
    for (const key in activity.counts) {
      // Initialize the array for this activity if it doesn't exist yet
      if (!(key in activityDict)) {
        activityDict[key] = [];
      }

      // Add the count for this date to the array for this activity
      activityDict[key].push({
        date: activity.taken_at,
        count: activity.counts[key],
      });
    }
  }

  // Sort each activity array by date
  for (const activity in activityDict) {
    activityDict[activity].sort((a, b) => (a.date > b.date ? 1 : -1));
  }

  return activityDict;
}
export function getTopActivitiesByCount(activities: Activities[]) {
  let counts: Record<string, number> = {};
  // Then we loop through each activity in the data...
  activities.forEach((activity: Activities) => {
    // ...and for each activity, we loop through its counts...
    for (let key in activity.counts) {
      // If this activity hasn't been added to the counts object yet, add it with a starting count of 0.
      if (!counts[key]) counts[key] = 0;
      // Add the count for this activity to the total.
      counts[key] += activity.counts[key];
    }
  });

  // Now we need to sort the counts. First, we convert the object to an array of [activity, count] pairs.
  let sortedCounts = Object.entries(counts)
    // Then we sort the array. The sort function takes two elements at a time (a and b)...
    .sort((a, b) => b[1] - a[1]); // ...and sorts them based on their counts. The result is an array sorted in descending order by count.

  // Finally, we log the sorted array to the console so you can see the result.
  return sortedCounts;
}
