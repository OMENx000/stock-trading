#include <iostream>


// operator overloading means we are changing how some opeartor will behave
class INT {
    // class that will change the basic add and substract operator and will swap the both
    int x;

    public:
        // constructors
        INT(int i) :x{i} {}
        INT() :x{0} {}

        // operator[sign] is used to overload
        int operator+(INT i, INT j)
        {
            return i.x - j.x;
        }

};

int main()
{

}