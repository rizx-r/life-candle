import unittest
from models import UserInput, LifeDestinyResult, KLinePoint, AnalysisData
from random_gen import generate_random_life_result

class TestRandomGenUserInput(unittest.TestCase):
    def make_input(self, birth_year, start_age):
        return UserInput(
            name="测试",
            gender="Male",
            birthYear=birth_year,
            yearPillar="甲子",
            monthPillar="丙寅",
            dayPillar="戊辰",
            hourPillar="壬戌",
            startAge=start_age,
            firstDaYun="丁卯",
            modelName="",
            apiBaseUrl="",
            apiKey="random"
        )

    def test_accepts_userinput_and_returns_result(self):
        ui = self.make_input(1990, 1)
        result = generate_random_life_result(ui)
        self.assertIsInstance(result, LifeDestinyResult)
        self.assertTrue(len(result.chartData) > 0)
        first = result.chartData[0]
        self.assertIsInstance(first, KLinePoint)
        self.assertEqual(first.age, 1)
        self.assertEqual(first.year, 1990)
        self.assertIsInstance(result.analysis, AnalysisData)

    def test_string_year_and_age_coercion(self):
        ui = self.make_input("2000", "3")
        result = generate_random_life_result(ui)
        first = result.chartData[0]
        self.assertEqual(first.age, 3)
        self.assertEqual(first.year, 2000)

    def test_rejects_non_userinput(self):
        with self.assertRaises(TypeError):
            generate_random_life_result({"birthYear": 1990, "startAge": 1})  # dict
        with self.assertRaises(TypeError):
            generate_random_life_result(None)  # None
        with self.assertRaises(TypeError):
            generate_random_life_result(123)  # wrong type

if __name__ == "__main__":
    unittest.main()
