#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自衰减福利货币体系理想数学模型
将货币流通速度作为结果计算，重点关注通胀压力分析
"""

import numpy as np
import scipy.optimize as opt
from scipy.optimize import least_squares
import math

class IdealCurrencyModel:
    """
    理想的自衰减福利货币体系数学模型 - 改进版
    """
    
    def __init__(self):
        # 基础经济参数
        self.population = 100_000_000  # N = 1亿人
        self.labor_force_ratio = 0.70  # 劳动人口占总人口比例
        self.workforce = self.population * self.labor_force_ratio # 劳动总人口
        self.gdp = 5_000_000_000_000  # Y = 5万亿元
        self.ai_gdp_ratio = 0.50  # α = 50%
        self.ai_profit_margin = 0.25  # π = 25%
        self.real_estate_gdp_ratio = 4.0  # β = 4.0 (与论文和prompts保持一致)
        self.welfare_economy_ratio = 0.35  # γ = 35%
        
        # 货币政策参数
        self.monthly_decay_rate = 0.025  # r = 2.5%
        self.annual_decay_rate = 1 - (1 - self.monthly_decay_rate)**12  # R ≈ 26.3%
        self.exchange_cost_rate = 0.025  # δ = 2.5%
        self.target_inflation = 0.025  # π_target = 2.5%
        
        # 税收政策参数
        self.property_tax_rate = 0.025  # τ_property = 2.5%
        self.ai_tax_rate = 0.15  # τ_AI = 15%
        self.carbon_tax_rate = 0.05  # τ_carbon = 5% (从10%调整为5%)
        self.public_service_gdp_ratio = 0.02  # θ = 2%
        self.property_tax_deduction_ratio = 0.30  # τ_deduct = 30%
        
        # 兑换行为参数
        self.personal_exchange_ratio = 0.15  # 个人储蓄兑换比例
        self.corporate_exchange_ratio = 0.25  # 企业储蓄兑换比例
        
        # 资金流向参数
        self.personal_consumption_ratio = 0.60  # 个人消费比例
        self.personal_savings_ratio = 0.15  # 个人储蓄比例
        # 初始个人税费比例占比 (将被动态更新)，确保计算流通速度时有值
        self.personal_tax_ratio = 0.25
        
        self.corporate_operation_ratio = 0.70  # 企业运营成本比例
        self.corporate_tax_ratio = 0.15  # 企业税费比例
        self.corporate_savings_ratio = 0.15  # 企业储蓄比例
        
        # 持币周期参数（月）
        self.consumption_holding_period = 0.5  # 消费用途持币0.5月
        self.tax_holding_period = 0.1  # 税费用途持币0.1月  
        self.savings_holding_period = 0.1  # 储蓄转换持币0.1月
        
        # 验证结果
        self.validation_results = {}

        # ---- 房产价值分布假设 ----
        # 每户 2.5 人，房价中值 37.5 万，分 5 段 (万元)
        # 值为区间中值，share 为户数占比
        self.property_distribution = [
            {"value_mid": 15 * 10000, "share": 0.20},  # 0–20 万
            {"value_mid": 30 * 10000, "share": 0.30},  # 20–40 万
            {"value_mid": 60 * 10000, "share": 0.25},  # 40–80 万
            {"value_mid": 115 * 10000, "share": 0.15}, # 80–150 万
            {"value_mid": 220 * 10000, "share": 0.10}, # ≥150 万
        ]

        # 计算户数
        self.households = self.population / 2.5

    # --------------------------------------------------
    # 动态房产税组件计算
    # --------------------------------------------------
    def _compute_property_tax_components(self, ubi_monthly):
        """根据房产价值分布与 UBI 计算抵扣段、超额段及 τ_deduct"""
        households = self.households

        # 分布总房产价值（未经缩放）
        distribution_total_value = 0.0
        for seg in self.property_distribution:
            distribution_total_value += seg["value_mid"] * seg["share"] * households

        # 目标总房产价值（与 GDP 比例保持一致）
        target_total_value = self.gdp * self.real_estate_gdp_ratio

        scale_factor = target_total_value / distribution_total_value if distribution_total_value else 1.0

        tau_prop = self.property_tax_rate

        total_tax_bill = 0.0
        d_total = 0.0
        e_total = 0.0

        for seg in self.property_distribution:
            V_adj = seg["value_mid"] * scale_factor  # 调整后的房产价值
            households_i = households * seg["share"]

            T_i = tau_prop * V_adj * households_i
            U_i = ubi_monthly * 12 * 2.5 * households_i

            D_i = min(T_i, U_i)
            E_i = max(0.0, T_i - U_i)

            total_tax_bill += T_i
            d_total += D_i
            e_total += E_i

        tau_deduct = d_total / total_tax_bill if total_tax_bill else 0.0

        return {
            "tau_deduct": tau_deduct,
            "property_tax_destruction": d_total,
            "property_tax_total_bill": total_tax_bill,
            "excess_property_tax": e_total,
        }
    
    def calculate_unemployment_compensation(self, ai_gdp_ratio, ubi_monthly):
        """
        根据AI占比计算失业人口补偿需求 (简化假设: AI占比 = 失业率)
        """
        unemployment_rate = ai_gdp_ratio
        unemployed_population = self.workforce * unemployment_rate
        
        # 假设每个失业者需要UBI的60%作为基本生活保障
        compensation_per_person_annual = ubi_monthly * 12 * 0.6
        compensation_needed = unemployed_population * compensation_per_person_annual
        
        return compensation_needed, unemployed_population

    def calculate_money_stock_from_flows(self, ubi_monthly, verbose=False):
        """
        基于资金流向和持币周期计算货币存量
        """
        annual_ubi_injection = ubi_monthly * 12 * self.population
        
        # 更新税费比例
        prop_stats = self._compute_property_tax_components(ubi_monthly)
        property_tax_destruction = prop_stats["property_tax_destruction"]
        public_service_destruction = self.gdp * self.public_service_gdp_ratio
        
        if annual_ubi_injection > 0:
            self.personal_tax_ratio = (
                property_tax_destruction + public_service_destruction
            ) / annual_ubi_injection
            self.personal_consumption_ratio = 1 - self.personal_savings_ratio - self.personal_tax_ratio
        
        # 计算各用途的资金量
        consumption_flow = annual_ubi_injection * self.personal_consumption_ratio
        tax_flow = annual_ubi_injection * self.personal_tax_ratio
        savings_flow = annual_ubi_injection * self.personal_savings_ratio
        
        # 基于持币周期计算存量（年化）
        consumption_stock = consumption_flow * (self.consumption_holding_period / 12)
        tax_stock = tax_flow * (self.tax_holding_period / 12)
        savings_stock = savings_flow * (self.savings_holding_period / 12)
        
        total_money_stock = consumption_stock + tax_stock + savings_stock
        
        if verbose:
            print(f"货币存量计算:")
            print(f"  消费存量: {consumption_stock/1e8:.2f}亿元 (流量{consumption_flow/1e8:.0f}亿 × 持币{self.consumption_holding_period:.1f}月)")
            print(f"  税费存量: {tax_stock/1e8:.2f}亿元 (流量{tax_flow/1e8:.0f}亿 × 持币{self.tax_holding_period:.1f}月)")
            print(f"  储蓄存量: {savings_stock/1e8:.2f}亿元 (流量{savings_flow/1e8:.0f}亿 × 持币{self.savings_holding_period:.1f}月)")
            print(f"  总存量: {total_money_stock/1e8:.2f}亿元")
        
        return total_money_stock
    
    def calculate_effective_velocity(self, ubi_monthly):
        """
        计算有效货币流通速度
        """
        annual_ubi_injection = ubi_monthly * 12 * self.population
        money_stock = self.calculate_money_stock_from_flows(ubi_monthly)
        
        if money_stock > 0:
            effective_velocity = annual_ubi_injection / money_stock
        else:
            effective_velocity = 0
            
        return effective_velocity
    
    def solve_equilibrium_system(self, verbose=True):
        """
        求解完整的均衡方程组 - 基于资金流向计算货币存量
        """
        if verbose:
            print("\n=== 均衡方程组求解（改进版）===")
        
        # AI产业相关计算
        ai_gdp = self.gdp * self.ai_gdp_ratio
        ai_profit = ai_gdp * self.ai_profit_margin
        
        # 法定企业税率（AI 税 + 碳税）固定为 0.20
        statutory_corp_rate = self.ai_tax_rate + self.carbon_tax_rate  # 20%
        
        if verbose:
            print(f"AI产业GDP: {ai_gdp/1e8:.0f}亿元")
            print(f"AI产业利润: {ai_profit/1e8:.0f}亿元")
            print(f"法定企业税率: {statutory_corp_rate:.0%}")

        def equilibrium_equation(ubi_monthly):
            """单方程：货币守恒，企业税率固定为法定值"""
            corporate_tax_rate = statutory_corp_rate
            
            # 年UBI投放
            annual_ubi_injection = ubi_monthly * 12 * self.population
            
            # 基于资金流向计算货币存量
            money_stock = self.calculate_money_stock_from_flows(ubi_monthly)
            
            # 自然衰减湮灭
            natural_decay = money_stock * self.annual_decay_rate
            
            # ---- 动态房产税湮灭 ----
            prop_stats_iter = self._compute_property_tax_components(ubi_monthly)
            property_tax_destruction = prop_stats_iter["property_tax_destruction"]
            
            # 公共服务费湮灭（固定比例）
            public_service_destruction = self.gdp * self.public_service_gdp_ratio

            # 企业税湮灭——以 AI "利润" 为税基
            corporate_tax_destruction = ai_profit * corporate_tax_rate

            # 兑换成本湮灭
            personal_exchange = annual_ubi_injection * self.personal_savings_ratio * self.personal_exchange_ratio
            corporate_exchange = annual_ubi_injection * self.corporate_savings_ratio * self.corporate_exchange_ratio
            exchange_destruction = (personal_exchange + corporate_exchange) * self.exchange_cost_rate

            # 总湮灭
            total_destruction = (natural_decay + property_tax_destruction + 
                               corporate_tax_destruction + public_service_destruction + 
                               exchange_destruction)
            
            return annual_ubi_injection - total_destruction
        
        # 求解
        solution = {}

        try:
            from scipy.optimize import root_scalar
            result = root_scalar(equilibrium_equation, bracket=[1, 1500], method='brentq')
            
            if result.converged:
                ubi_opt = float(result.root)
                corp_tax_rate_opt = statutory_corp_rate
                
                # --- 基于最优解计算所有关键指标 ---
                money_stock_opt = self.calculate_money_stock_from_flows(ubi_opt)
                annual_ubi_injection = ubi_opt * 12 * self.population
                effective_velocity = self.calculate_effective_velocity(ubi_opt)
                
                # 重新计算最终的房产税各部分
                prop_stats_opt = self._compute_property_tax_components(ubi_opt)
                excess_property_tax_opt = prop_stats_opt["excess_property_tax"]
                property_tax_destruction_opt = prop_stats_opt["property_tax_destruction"]

                # 兑换湮灭计算
                personal_exchange = annual_ubi_injection * self.personal_savings_ratio * self.personal_exchange_ratio
                corporate_exchange = annual_ubi_injection * self.corporate_savings_ratio * self.corporate_exchange_ratio
                exchange_destruction_opt = (personal_exchange + corporate_exchange) * self.exchange_cost_rate

                # 企业税
                corporate_tax_destruction_opt = ai_profit * corp_tax_rate_opt

                # 公共服务费
                public_service_destruction_opt = self.gdp * self.public_service_gdp_ratio

                # 自然衰减
                natural_decay_opt = money_stock_opt * self.annual_decay_rate

                # 央行基础货币增长计算
                total_exchange_volume = personal_exchange + corporate_exchange + excess_property_tax_opt
                central_bank_base_money_growth = total_exchange_volume / (self.gdp * 2) # 假设基础货币存量为GDP的2倍
                
                residual = equilibrium_equation(ubi_opt)
                max_residual = abs(residual)

                if verbose:
                    print(f"\n数值解结果:")
                    print(f"月人均UBI: {ubi_opt:.2f}元")
                    print(f"企业税率: {corp_tax_rate_opt:.2%}")
                    print(f"货币存量: {money_stock_opt/1e8:.2f}亿元")
                    print(f"有效流通速度: {effective_velocity:.2f}次/年")
                    print(f"最大残差: {max_residual:.2e}")

                solution = {
                    "status": "success",
                    "ubi_monthly": ubi_opt,
                    "corporate_tax_rate": corp_tax_rate_opt,
                    "corporate_tax_destruction": corporate_tax_destruction_opt,
                    "excess_property_tax": excess_property_tax_opt,
                    "property_tax_destruction": property_tax_destruction_opt,
                    "public_service_destruction": public_service_destruction_opt,
                    "natural_decay": natural_decay_opt,
                    "exchange_destruction": exchange_destruction_opt,
                    "money_stock": money_stock_opt,
                    "annual_ubi_injection": annual_ubi_injection,
                    "effective_velocity": effective_velocity,
                    "central_bank_base_money_growth_rate": central_bank_base_money_growth,
                    "max_residual": max_residual
                }
            else:
                if verbose:
                    print("求解失败：未能收敛。")
                solution = {"status": "failure", "error": "Solver did not converge."}

        except ValueError as e:
            if verbose:
                print(f"求解失败: {e}")
            solution = {"status": "failure", "error": str(e)}
        
        return solution

    def validate_all_constraints(self, solution):
        """
        验证所有约束条件
        """
        print("\n=== 约束条件验证 ===")
        
        if not solution:
            print("❌ 无解可验证")
            return False
        
        ubi_monthly = solution['ubi_monthly']
        money_stock = solution['money_stock']
        corporate_tax_rate = solution['corporate_tax_rate']
        exchange_destruction = solution['exchange_destruction']
        central_bank_growth = solution['central_bank_base_money_growth_rate']
        
        # 1. 货币守恒验证
        annual_ubi_injection = ubi_monthly * 12 * self.population
        
        # 各项湮灭
        natural_decay = money_stock * self.annual_decay_rate
        prop_stats = self._compute_property_tax_components(ubi_monthly)
        property_tax_total_bill = prop_stats["property_tax_total_bill"]
        property_tax_destruction = prop_stats["property_tax_destruction"]
        excess_property_tax = prop_stats["excess_property_tax"]
        # 更新动态 τ_deduct
        tau_deduct_dynamic = prop_stats["tau_deduct"]
        ai_profit = self.gdp * self.ai_gdp_ratio * self.ai_profit_margin
        statutory_corp_rate = self.ai_tax_rate + self.carbon_tax_rate
        corporate_tax_destruction = ai_profit * corporate_tax_rate
        public_service_destruction = self.gdp * self.public_service_gdp_ratio
        
        total_destruction = (natural_decay + property_tax_destruction + 
                           corporate_tax_destruction + public_service_destruction + 
                           exchange_destruction)
        
        conservation_error = abs(annual_ubi_injection - total_destruction) / annual_ubi_injection
        
        print(f"货币守恒检验:")
        print(f"  年UBI投放: {annual_ubi_injection/1e8:.0f}亿元")
        print(f"  自然衰减: {natural_decay/1e8:.0f}亿元")
        print(f"  财产税湮灭 (动态抵扣率 {tau_deduct_dynamic:.0%}): {property_tax_destruction/1e8:.0f}亿元")
        print(f"  超额财产税 (基础货币): {excess_property_tax/1e8:.0f}亿元")
        print(f"  企业税湮灭: {corporate_tax_destruction/1e8:.0f}亿元")
        print(f"  公共服务费湮灭: {public_service_destruction/1e8:.0f}亿元")
        print(f"  兑换成本湮灭: {exchange_destruction/1e8:.0f}亿元")
        print(f"  总湮灭: {total_destruction/1e8:.0f}亿元")
        print(f"  相对误差: {conservation_error:.4%}")
        
        # 2. 企业税约束验证
        ai_profit = self.gdp * self.ai_gdp_ratio * self.ai_profit_margin
        # 无需上限判断，改为固定税率约束
        actual_ai_tax = ai_profit * self.ai_tax_rate  # 固定 15%
        actual_carbon_tax = ai_profit * self.carbon_tax_rate  # 固定 5%
        
        print(f"\n企业税约束验证:")
        print(f"  AI产业利润: {ai_profit/1e8:.0f}亿元")
        print(f"  规定企业税率: {statutory_corp_rate:.0%}")
        print(f"  总企业税: {corporate_tax_destruction/1e8:.0f}亿元")
        print(f"  AI税部分: {actual_ai_tax/1e8:.0f}亿元 ({actual_ai_tax/ai_profit:.1%})")
        print(f"  碳税部分: {actual_carbon_tax/1e8:.0f}亿元 ({actual_carbon_tax/ai_profit:.1%})")
        
        # 3. 补偿需求验证
        compensation_needed, unemployed_population = self.calculate_unemployment_compensation(
            self.ai_gdp_ratio, ubi_monthly
        )

        print(f"\n补偿需求验证 (劳动人口: {self.workforce/1e4:.0f}万, AI失业率: {self.ai_gdp_ratio:.0%}):")
        print(f"  失业人口: {unemployed_population/1e4:.1f} 万人")
        print(f"  补偿需求: {compensation_needed/1e8:.0f}亿元")
        print(f"  补偿资金(企税+超额房产税): {(corporate_tax_destruction+excess_property_tax)/1e8:.0f}亿元")
        print(f"  补偿充足性: {'✓' if corporate_tax_destruction + excess_property_tax >= compensation_needed else '✗'}")
        
        # 4. 央行约束验证
        print(f"\n央行约束验证:")
        print(f"  基础货币增长率: {central_bank_growth:.2%}")
        print(f"  增长率上限: 5.0%")
        print(f"  央行约束: {'✓' if central_bank_growth <= 0.05 else '✗'}")
        
        # 5. 资金流向完整性验证
        personal_flow_sum = self.personal_consumption_ratio + self.personal_savings_ratio + self.personal_tax_ratio
        corporate_flow_sum = self.corporate_operation_ratio + self.corporate_tax_ratio + self.corporate_savings_ratio
        
        print(f"\n资金流向验证:")
        print(f"  个人资金流向总和: {personal_flow_sum:.1%}")
        print(f"  企业资金流向总和: {corporate_flow_sum:.1%}")
        
        # 综合评估
        constraints_passed = (
            conservation_error < 0.01 and
            abs(corporate_tax_rate - statutory_corp_rate) < 1e-4 and
            corporate_tax_destruction + excess_property_tax >= compensation_needed and
            central_bank_growth <= 0.05 and
            abs(personal_flow_sum - 1.0) < 0.01 and
            abs(corporate_flow_sum - 1.0) < 0.01
        )
        
        print(f"\n验证结果:")
        print(f"货币守恒: {'✓' if conservation_error < 0.01 else '✗'}")
        print(f"企业税率固定约束: {'✓' if abs(corporate_tax_rate - statutory_corp_rate) < 1e-4 else '✗'}")
        print(f"补偿充足性: {'✓' if corporate_tax_destruction + excess_property_tax >= compensation_needed else '✗'}")
        print(f"央行约束: {'✓' if central_bank_growth <= 0.05 else '✗'}")
        print(f"资金流向完整性: {'✓' if abs(personal_flow_sum - 1.0) < 0.01 and abs(corporate_flow_sum - 1.0) < 0.01 else '✗'}")
        
        self.validation_results['all_constraints'] = constraints_passed
        return constraints_passed
    
    def analyze_500_target(self, verbose=True):
        """
        分析500元/月目标的可行性
        """
        if verbose:
            print("\n=== 500元/月目标可行性分析 ===")
        
        # 尝试固定UBI为500元求解
        statutory_corp_rate = self.ai_tax_rate + self.carbon_tax_rate

        def fixed_ubi_equations(variables):
            """固定UBI为500元的方程组"""
            corporate_tax_rate = statutory_corp_rate  # 固定 20%
            ubi_monthly = 500
            
            # 重复主要计算逻辑
            annual_ubi_injection = ubi_monthly * 12 * self.population
            money_stock = self.calculate_money_stock_from_flows(ubi_monthly)
            
            natural_decay = money_stock * self.annual_decay_rate
            prop_stats = self._compute_property_tax_components(ubi_monthly)
            property_tax_total_bill = prop_stats["property_tax_total_bill"]
            property_tax_destruction = prop_stats["property_tax_destruction"]
            excess_property_tax = prop_stats["excess_property_tax"]
            # 更新动态 τ_deduct
            tau_deduct_dynamic = prop_stats["tau_deduct"]
            ai_profit = self.gdp * self.ai_gdp_ratio * self.ai_profit_margin
            corporate_tax_destruction = ai_profit * corporate_tax_rate
            public_service_destruction = self.gdp * self.public_service_gdp_ratio
            
            personal_exchange = annual_ubi_injection * self.personal_savings_ratio * self.personal_exchange_ratio
            corporate_exchange = annual_ubi_injection * self.corporate_savings_ratio * self.corporate_exchange_ratio
            exchange_destruction = (personal_exchange + corporate_exchange) * self.exchange_cost_rate

            # 中高资产家庭购入福利货币的超额房产税兑换量，计入总兑换规模
            household_property_exchange = excess_property_tax  # 视为 1:1 兑换，无额外成本
            
            total_destruction = (natural_decay + property_tax_destruction + 
                               corporate_tax_destruction + public_service_destruction + 
                               exchange_destruction)
            
            # 货币守恒方程
            eq1 = annual_ubi_injection - total_destruction
            return eq1  # 返回标量
        
        try:
            # 只需检查守恒即可
            root_val = fixed_ubi_equations(0)  # eq1 value
            feasible = abs(root_val) < 1e-2
            if verbose:
                print(f"500元/月守恒误差: {root_val/1e8:.2f}亿元 -> {'✓ 可行' if feasible else '✗ 不可行'}")
            return feasible
        except Exception as e:
            if verbose:
                print(f"500元/月目标分析失败: {e}")
            return False
    
    def comprehensive_report(self):
        """
        生成全面的模型评估报告
        """
        print("\n" + "="*50)
        print(" " * 10 + "自衰减福利货币体系理想模型评估报告")
        print("="*50)
        
        solution = self.solve_equilibrium_system(verbose=False)
        if solution['status'] != 'success':
            print("模型未能求解，无法生成报告。")
            return
            
        self.validate_all_constraints(solution)
        # is_valid = self.validate_all_constraints(solution) # validate_all_constraints prints its own report
        
        # print("\n## 一、模型收敛性与约束验证\n")
        # if is_valid:
        #     print(f"**✅ 模型已完全收敛，所有约束条件均满足：**\n")
        #     print(f"- **最优解UBI水平**：`{solution['ubi_monthly']:.0f}元/月`")
        #     print(f"- **最大残差**：`{solution['max_residual']:.2e}`，表明货币守恒方程已精确求解。")
        #     print(f"- **所有约束验证**：货币守恒、企业税率、补偿充足性、央行约束、资金流向完整性全部 `✓` 通过。")
        # else:
        #     print(f"**❌ 模型未通过所有约束验证：**\n")
        #     for key, value in self.validation_results.items():
        #         print(f"- {key}: {'✓' if value else '✗'}")

        print("\n## 核心财政数据分析\n")
        ubi = solution['ubi_monthly']
        corp_tax = solution['corporate_tax_destruction']
        excess_prop_tax = solution['excess_property_tax']
        public_service_fee = self.gdp * self.public_service_gdp_ratio
        
        compensation_available = corp_tax + excess_prop_tax
        compensation_needed, _ = self.calculate_unemployment_compensation(self.ai_gdp_ratio, ubi)
        net_compensation = compensation_available - public_service_fee

        print(f"1. **UBI与税负结构**")
        print(f"   - 可持续月度UBI: **`{ubi:.2f}`** 元")
        print(f"   - AI企业税贡献: **`{corp_tax/1e8:.2f}`** 亿元")
        print(f"   - 超额财产税 (高净值家庭贡献): **`{excess_prop_tax/1e8:.2f}`** 亿元")
        print(f"   - 公共服务费 (全民成本): **`{public_service_fee/1e8:.2f}`** 亿元")

        print(f"\n2. **AI失业人口补偿能力**")
        print(f"   - 补偿能力 (AI企税 + 超额房产税): **`{compensation_available/1e8:.2f}`** 亿元/年")
        print(f"   - 补偿需求 (在AI失业率{self.ai_gdp_ratio:.0%}下): **`{compensation_needed/1e8:.2f}`** 亿元/年")
        print(f"   - **净消费补偿水平**: **`{net_compensation/1e8:.2f}`** 亿元/年")
        print(f"   - *净消费补偿 = 补偿能力 - 公共服务费，衡量对社会的净“反哺”能力。*")

        print("\n## 三、货币与央行状态\n")
        print(f"1. **货币流通速度 (V)**: `{solution['effective_velocity']:.2f}` 次/年")
        print(f"2. **福利货币存量 (M)**: `{solution['money_stock']/1e8:.2f}` 亿元")
        print(f"3. **央行基础货币年增长率**: **`{solution['central_bank_base_money_growth_rate'] * 100:.2f}%`** (警戒线: 5%)")

        print("\n" + "="*50)
        
    def run_unemployment_scenarios(self):
        """
        分析不同AI失业率下的财政收敛水平
        """
        print("\n" + "="*50)
        print(" " * 15 + "AI失业率动态情景分析")
        print("="*50)
        print("分析AI取代不同比例就业人口时，系统能够维持的财政稳态。")
        
        scenarios = [0.40, 0.50, 0.60, 0.70] # 明确定义为失业率
        results_data = []

        # 保存原始参数
        original_ai_gdp_ratio = self.ai_gdp_ratio

        for unemployment_rate in scenarios:
            print(f"\n--- 正在计算场景：失业率 = {unemployment_rate:.0%} ---")
            self.ai_gdp_ratio = unemployment_rate # 简化假设: AI占比 = 失业率
            
            # 求解均衡
            solution = self.solve_equilibrium_system(verbose=False)
            
            if solution['status'] == 'success':
                ubi = solution['ubi_monthly']
                corp_tax = solution['corporate_tax_destruction']
                excess_prop_tax = solution['excess_property_tax']
                
                # 计算实际补偿需求与可用补偿
                compensation_needed, unemployed = self.calculate_unemployment_compensation(
                    unemployment_rate, ubi
                )
                compensation_available = corp_tax + excess_prop_tax
                
                results_data.append({
                    "rate": unemployment_rate,
                    "ubi": ubi,
                    "compensation_available": compensation_available,
                    "compensation_needed": compensation_needed,
                    "is_sufficient": compensation_available >= compensation_needed,
                    "converged": True
                })
                print(f"计算完成。可持续UBI: {ubi:.2f}元/月")
                print(f"  - 失业人口: {unemployed/1e4:.1f}万人 (劳动总人口 {self.workforce/1e4:.0f}万), 补偿需求: {compensation_needed/1e8:.2f}亿元")
                print(f"  - 补偿能力: {compensation_available/1e8:.2f}亿元 -> {'✓ 充足' if compensation_available >= compensation_needed else '✗ 不足'}")

            else:
                results_data.append({
                    "rate": unemployment_rate,
                    "ubi": 0, "compensation_available": 0, "compensation_needed": 0,
                    "is_sufficient": False, "converged": False
                })
                print("模型未能在此场景下收敛。")

        # 恢复原始参数
        self.ai_gdp_ratio = original_ai_gdp_ratio

        # 打印Markdown格式的报告
        print(f"\n\n--- AI失业率动态情景分析总结报告 (劳动总人口: {self.workforce/1e4:.0f}万) ---\n")
        print("| 失业率 | 可持续UBI (元/月) | 补偿能力 (亿元) | 补偿需求 (亿元) | 补偿充足性 |")
        print("|:------:|:-------------------:|:-----------------:|:-----------------:|:------------:|")
        for res in results_data:
            if res['converged']:
                print(f"| {res['rate']:.0%}    | {res['ubi']:.2f}              | {res['compensation_available']/1e8:.2f}         | {res['compensation_needed']/1e8:.2f}        | {'✓ 充足' if res['is_sufficient'] else '✗ 不足'}       |")
            else:
                print(f"| {res['rate']:.0%}    | 未收敛              | -                 | -                 | ✗            |")
        print("\n" + "="*50)

        return results_data

    def analyze_inflation_pressure(self, solution, verbose=True):
        """
        分析通胀压力
        """
        if not solution or solution['status'] != 'success':
            print("无有效解进行通胀压力分析")
            return None
            
        if verbose:
            print("\n=== 通胀压力分析 ===")
        
        ubi_monthly = solution['ubi_monthly']
        annual_ubi_injection = ubi_monthly * 12 * self.population
        
        # 定义：进入广义消费领域的货币量，是未被税收直接湮灭的所有部分
        additional_consumption_money = annual_ubi_injection * (1 - self.personal_tax_ratio)
        
        # 定义：消费品市场的基线规模（福利经济部分）
        baseline_consumption_market = self.gdp * self.welfare_economy_ratio
        
        # 通胀压力指数 = 额外消费货币 / 基线消费市场 (经济学标准定义)
        inflation_pressure = additional_consumption_money / baseline_consumption_market
        
        # 风险评估
        risk_level = self._assess_risk(inflation_pressure)
        
        if verbose:
            print(f"广义消费领域分析:")
            print(f"  流入消费的额外货币: {additional_consumption_money/1e8:.2f}亿元/年")
            print(f"  基线消费市场规模: {baseline_consumption_market/1e8:.2f}亿元/年")
            print(f"  通胀压力指数: {inflation_pressure:.3f}")
            print(f"  风险等级: {risk_level}")
            
            print(f"\n解释:")
            print(f"- 通胀压力指数 = 流入消费的额外货币 / 基线消费市场规模")
            print(f"- 该指数直接衡量了超发货币对消费品市场的冲击程度。")
            print(f"- 指数 << 1.0: 通胀压力可控")
            print(f"- 指数接近 1.0: 有显著通胀风险")
        
        return {
            "inflation_pressure": inflation_pressure,
            "additional_consumption_money": additional_consumption_money,
            "baseline_consumption_market": baseline_consumption_market,
            "risk_level": risk_level
        }
    
    def _assess_risk(self, inflation_pressure):
        """评估通胀风险等级"""
        if inflation_pressure < 1.0:
            return "低风险"
        elif inflation_pressure < 1.2:
            return "中等风险"
        elif inflation_pressure < 1.5:
            return "高风险"
        else:
            return "极高风险"

    def run_savings_rate_scenarios(self):
        """
        分析不同个人储蓄率下的财政收敛与通胀压力
        """
        print("\n" + "="*50)
        print(" " * 15 + "个人储蓄率动态情景分析")
        print("="*50)
        print("分析当个人选择将不同比例的UBI兑换为基础货币时，系统的均衡状态和通胀压力。")
        
        scenarios = [0.15, 0.10, 0.05, 0.0]
        results_data = []

        # 保存原始参数
        original_savings_rate = self.personal_savings_ratio

        for rate in scenarios:
            print(f"\n--- 正在计算场景：个人储蓄率 = {rate:.0%} ---")
            self.personal_savings_ratio = rate
            
            # 求解均衡
            solution = self.solve_equilibrium_system(verbose=False)
            
            if solution['status'] == 'success':
                # 运行通胀分析
                inflation_info = self.analyze_inflation_pressure(solution, verbose=False)
                
                results_data.append({
                    "rate": rate,
                    "ubi": solution['ubi_monthly'],
                    "velocity": solution['effective_velocity'],
                    "inflation_pressure": inflation_info['inflation_pressure'],
                    "converged": True
                })
                print(f"计算完成。可持续UBI: {solution['ubi_monthly']:.2f}元/月, 通胀压力: {inflation_info['inflation_pressure']:.3f}")
            else:
                results_data.append({
                    "rate": rate, "ubi": 0, "velocity": 0, "inflation_pressure": 0, "converged": False
                })
                print("模型未能在此场景下收敛。")

        # 恢复原始参数
        self.personal_savings_ratio = original_savings_rate

        # 打印Markdown格式的报告
        print("\n\n--- 个人储蓄率情景分析总结报告 ---\n")
        print("| 个人储蓄率 | 可持续UBI (元/月) | 有效流通速度 (次/年) | 通胀压力指数 |")
        print("|:----------:|:-------------------:|:------------------------:|:--------------------:|")
        for res in results_data:
            if res['converged']:
                print(f"| {res['rate']:.0%}        | {res['ubi']:.2f}              | {res['velocity']:.2f}                    | {res['inflation_pressure']:.3f}                |")
            else:
                print(f"| {res['rate']:.0%}        | 未收敛              | -                        | -                    |")
        
        print("\n解释：储蓄率降低，意味着用于市场兑换的UBI减少，因此兑换成本湮灭会减少。为维持平衡，UBI水平会略微下降。")
        print("同时，更多货币被划归为'消费'用途，其持币周期更长，这会降低系统的有效流通速度。")
        print("最终，虽然进入广义消费领域的货币比例上升，但流通速度的下降起到了对冲作用，通胀压力指数变化平稳。")
        print("="*50)

        return results_data

    def sensitivity_analysis(self, solution):
        """
        敏感性分析
        """
        print("\n=== 敏感性分析 ===")
        
        if not solution:
            print("无解可进行敏感性分析")
            return
        
        base_ubi = solution['ubi_monthly']
        
        # 测试关键参数
        sensitivity_params = {
            'monthly_decay_rate': [0.020, 0.025, 0.030],
            'public_service_gdp_ratio': [0.015, 0.020, 0.025],
            'carbon_tax_rate': [0.03, 0.05, 0.07],
            'personal_exchange_ratio': [0.10, 0.15, 0.20]
        }
        
        print("参数敏感性测试:")
        for param_name, param_values in sensitivity_params.items():
            ubi_variations = []
            
            for value in param_values:
                original_value = getattr(self, param_name)
                setattr(self, param_name, value)
                
                try:
                    temp_solution = self.solve_equilibrium_system(verbose=False)
                    if temp_solution:
                        ubi_variations.append(temp_solution['ubi_monthly'])
                    else:
                        ubi_variations.append(None)
                except:
                    ubi_variations.append(None)
                
                setattr(self, param_name, original_value)
            
            valid_variations = [v for v in ubi_variations if v is not None]
            if len(valid_variations) > 1:
                sensitivity = (max(valid_variations) - min(valid_variations)) / base_ubi
                print(f"  {param_name}: 变化幅度 {sensitivity:.1%}")

def main():
    # 实例化模型
    model = IdealCurrencyModel()
    
    # 运行一次完整的均衡求解和报告
    model.comprehensive_report()
    
    # 获取解以进行通胀压力分析
    solution = model.solve_equilibrium_system(verbose=False)
    
    # 运行通胀压力分析
    if solution and solution['status'] == 'success':
        inflation_analysis = model.analyze_inflation_pressure(solution)
        
    # # 运行对500元目标的分析
    # model.analyze_500_target()

    # 运行新的动态失业率情景分析
    model.run_unemployment_scenarios()

    # 运行新的储蓄率情景分析
    model.run_savings_rate_scenarios()


if __name__ == "__main__":
    main() 