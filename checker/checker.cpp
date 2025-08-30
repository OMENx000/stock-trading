#include <pybind11/pybind11.h>
#include <string>
#include <vector>
using namespace std;

int longest_common_substring(const string& s1, const string& s2) {
    int n = s1.size(), m = s2.size();
    vector<vector<int>> dp(n+1, vector<int>(m+1, 0));
    int result = 0;
    for(int i=1;i<=n;i++) {
        for(int j=1;j<=m;j++) {
            if(s1[i-1] == s2[j-1]) {
                dp[i][j] = dp[i-1][j-1] + 1;
                result = max(result, dp[i][j]);
            }
        }
    }
    return result;
}

PYBIND11_MODULE(cpplcsu, m) {
    m.def("longest_common_substring", &longest_common_substring);
}
