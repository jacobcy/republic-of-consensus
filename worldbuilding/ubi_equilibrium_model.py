#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一经济模型计算器
该模型整合了宏观经济结构（digital_economy_calculator）与
自衰减福利货币的动态循环（currency_calculator），
旨在模拟一个包含双层UBI、货币衰减和财政平衡的完整数字经济体。
"""
import numpy as np
from scipy.optimize import root_scalar

class UnifiedEconomicModel:
    """
    统一的宏观经济与货币循环模型
    """
    
    def __init__(self, params=None):
        self._set_parameters(params)
        self.solution = self._solve_equilibrium()

    def _set_parameters(self, params):
        """设定模型参数，用户可覆盖默认值"""
        if params is None:
            params = {}
        
        default_params = {
            # === 宏观经济基本盘 ===
            "total_population": 100_000_000,
            "total_gdp": 5_000_000_000_000,
            "digital_economy_ratio": 0.70,

            # === 人口结构 ===
            "working_age_ratio": 0.7,
            "high_income_ratio_of_working": 2/7,
            "ubi_ratio_of_total": 0.5,
            
            # === 高净值群体收支 (占其总收入的比例) ===
            "high_income_per_capita_income": 100_000,
            "high_income_spending_ratios": {
                "digital_consumption": 0.5,
                "investment_savings": 0.5,
            },
            
            # === 福利货币(W-Cash)与UBI核心参数 ===
            "monthly_decay_rate": 0.025, # W-Cash月度衰减率
            "exchange_cost_rate": 0.025, # 兑换为基础货币的成本率
            
            # UBI群体支出与储蓄习惯 (占其总UBI收入)
            "ubi_spending_habits": {
                "digital_consumption": 0.6,
                "traditional_consumption": 0.2,
                "savings_exchange": 0.2, # 用于储蓄并兑换为基础货币的比例
            },

            # W-Cash 持币周期 (月)
            "wcash_holding_periods": {
                "consumption": 0.5, # 消费用途
                "tax": 0.1,         # 税费用图
                "savings": 0.1,     # 储蓄兑换用途
            },

            # === 企业与政府 ===
            # 数字经济成本结构 (占数字经济总量)
            "digital_cost_ratios": {
                "personnel": 0.40,      # 人力成本
                "operation": 0.20,      # 运营成本
                "attention_purchase": 0.05, # 注意力购买成本 (支付给UBI群体)
                "depreciation": 0.20,   # 折旧投资
                "tax": 0.05,            # 税收
            },

            # 财政政策
            "total_tax_to_digital_tax_ratio": 2.0, # 总税收相对数字经济税收的倍数
            "gov_spending_ratios": { # 政府支出占总税收的比例
                "base_ubi": 0.6,             # 基础UBI
                "digital_investment": 0.1,   # 数字经济投资
                "other_services": 0.3,       # 其他公共服务
            },
            # 全民服务费，作为W-Cash湮灭渠道，占GDP比例
            "public_service_fee_gdp_ratio": 0.02,
        }
        
        self.p = {**default_params, **(params or {})}
        self.p["annual_decay_rate"] = 1 - (1 - self.p["monthly_decay_rate"])**12

    def _solve_equilibrium(self):
        """解算均衡状态下的基础UBI水平"""

        def equilibrium_equation(base_ubi_monthly):
            # 1. 计算年度基础UBI总注入量 (这是W-Cash的来源)
            annual_base_ubi_injection = base_ubi_monthly * 12 * self.ubi_population
            
            # 2. 计算W-Cash货币存量
            # 首先，需要知道各类用途的资金流
            # 公共服务费需要从总注入中扣除，作为税收湮灭
            public_service_fee_destruction = self.p['public_service_fee_gdp_ratio'] * self.total_gdp
            
            # 个人税费流 = 公共服务费
            tax_flow = min(public_service_fee_destruction, annual_base_ubi_injection)
            
            # 储蓄流，基于总注入量
            savings_flow = annual_base_ubi_injection * self.p['ubi_spending_habits']['savings_exchange']
            
            # 消费流 = 总注入 - 税收 - 储蓄
            consumption_flow = annual_base_ubi_injection - tax_flow - savings_flow
            
            # 基于持币周期计算存量
            hp = self.p['wcash_holding_periods']
            consumption_stock = consumption_flow * (hp['consumption'] / 12)
            tax_stock = tax_flow * (hp['tax'] / 12)
            savings_stock = savings_flow * (hp['savings'] / 12)
            
            money_stock = consumption_stock + tax_stock + savings_stock
            
            # 3. 计算总湮灭量
            # a. 自然衰减
            natural_decay = money_stock * self.p['annual_decay_rate']
            
            # b. 兑换成本湮灭
            exchange_destruction = savings_flow * self.p['exchange_cost_rate']
            
            # c. 税收/服务费湮灭
            tax_destruction = tax_flow

            total_destruction = natural_decay + exchange_destruction + tax_destruction
            
            # 均衡条件：注入 = 湮灭
            return annual_base_ubi_injection - total_destruction

        # --- 前置计算 ---
        self.total_population = self.p['total_population']
        self.working_age_population = self.total_population * self.p['working_age_ratio']
        self.high_income_group = self.working_age_population * self.p['high_income_ratio_of_working']
        self.ubi_population = self.total_population * self.p['ubi_ratio_of_total']
        self.total_gdp = self.p['total_gdp']
        self.digital_economy_size = self.total_gdp * self.p['digital_economy_ratio']

        # 政府预算依赖于数字经济税收，而数字经济税收是固定的
        costs_ratios = self.p['digital_cost_ratios']
        digital_tax_revenue = self.digital_economy_size * costs_ratios['tax']
        total_tax_revenue = digital_tax_revenue * self.p['total_tax_to_digital_tax_ratio']
        
        # 计算可用于基础UBI的总资金
        available_for_base_ubi = total_tax_revenue * self.p['gov_spending_ratios']['base_ubi']
        
        # 如果财政无法支持任何UBI，则直接返回0
        if available_for_base_ubi <= 0 or self.ubi_population == 0:
            return self._calculate_final_metrics(0)
        
        # 理论上的最大UBI，用于设定求解区间
        theoretical_max_ubi = available_for_base_ubi / self.ubi_population / 12
        
        try:
            result = root_scalar(equilibrium_equation, bracket=[1, theoretical_max_ubi * 1.5], method='brentq')
            if result.converged:
                return self._calculate_final_metrics(result.root)
            else:
                 return {"status": "failure", "error": "Solver did not converge."}
        except ValueError as e:
            # 如果函数在区间两端同号，说明可能没有解或解在边界
            # 尝试在边界值检查
            if equilibrium_equation(1) * equilibrium_equation(theoretical_max_ubi) > 0:
                # 可能是注入永远大于或小于湮灭
                return self._calculate_final_metrics(theoretical_max_ubi) # 以理论上限作为结果
            return {"status": "failure", "error": str(e)}

    def _calculate_final_metrics(self, base_ubi_monthly):
        """基于解出的UBI，计算所有最终的经济指标"""
        res = {"status": "success", "base_ubi_monthly": base_ubi_monthly}

        # === UBI 完整构成 ===
        gov_budget = {}
        costs_ratios = self.p['digital_cost_ratios']
        gov_budget['digital_tax_revenue'] = self.digital_economy_size * costs_ratios['tax']
        gov_budget['total_tax_revenue'] = gov_budget['digital_tax_revenue'] * self.p['total_tax_to_digital_tax_ratio']
        gov_budget['spending_base_ubi'] = gov_budget['total_tax_revenue'] * self.p['gov_spending_ratios']['base_ubi']
        
        corporate_attention_spending = self.digital_economy_size * costs_ratios['attention_purchase']
        
        ubi_income = {}
        ubi_income['base_from_gov'] = base_ubi_monthly
        ubi_income['from_attention_purchase'] = (corporate_attention_spending / self.ubi_population / 12) if self.ubi_population else 0
        ubi_income['total_monthly'] = ubi_income['base_from_gov'] + ubi_income['from_attention_purchase']
        res['ubi_income'] = ubi_income

        # === 经济体各方收支平衡 ===
        # 1. UBI群体
        ubi_balance = {}
        total_monthly_income = ubi_income['total_monthly']
        habits = self.p['ubi_spending_habits']
        ubi_balance['income'] = total_monthly_income
        ubi_balance['spending_digital'] = total_monthly_income * habits['digital_consumption']
        ubi_balance['spending_traditional'] = total_monthly_income * habits['traditional_consumption']
        ubi_balance['savings'] = total_monthly_income * habits['savings_exchange']
        ubi_balance['unaccounted'] = total_monthly_income - sum([v for k,v in ubi_balance.items() if k != 'income'])
        res['ubi_balance_sheet'] = ubi_balance

        # 2. 高净值群体
        high_income_balance = {}
        high_income_balance['income_per_capita'] = self.p['high_income_per_capita_income']
        spending = self.p['high_income_spending_ratios']
        high_income_balance['spending_digital'] = high_income_balance['income_per_capita'] * spending['digital_consumption']
        high_income_balance['savings'] = high_income_balance['income_per_capita'] * spending['investment_savings']
        res['high_income_balance_sheet'] = high_income_balance

        # 3. 数字经济
        digital_econ_balance = {}
        # 收入
        rev = {}
        total_high_income = self.high_income_group * self.p['high_income_per_capita_income']
        rev['from_high_income'] = total_high_income * spending['digital_consumption']
        total_ubi_income_annual = ubi_income['total_monthly'] * 12 * self.ubi_population
        rev['from_ubi_group'] = total_ubi_income_annual * habits['digital_consumption']
        
        gov_spending_digital = gov_budget['total_tax_revenue'] * self.p['gov_spending_ratios']['digital_investment']
        rev['from_government'] = gov_spending_digital
        digital_econ_balance['revenue'] = rev
        
        # 成本
        costs = {}
        total_costs = 0
        for key, ratio in self.p['digital_cost_ratios'].items():
            cost_val = self.digital_economy_size * ratio
            costs[key] = cost_val
            total_costs += cost_val
        costs['gross_profit'] = self.digital_economy_size - total_costs
        digital_econ_balance['costs'] = costs
        
        rev['total_explicit'] = sum(rev.values())
        digital_econ_balance['revenue']['export_or_other'] = self.digital_economy_size - rev['total_explicit']
        res['digital_economy_balance_sheet'] = digital_econ_balance
        
        return res

    def generate_report(self):
        """生成综合报告"""
        if not self.solution or self.solution['status'] != 'success':
            print("模型未能求解，无法生成报告。")
            return

        sol = self.solution
        print("\n" + "="*80)
        print(" " * 25 + "统一经济模型评估报告")
        print("="*80)

        # --- UBI分析 ---
        ubi = sol['ubi_income']
        print("\n--- 1. UBI收入分析 (月人均) ---")
        print(f"  - 政府基础UBI (W-Cash注入): {ubi['base_from_gov']:.2f} 元")
        print(f"  - 企业注意力购买: {ubi['from_attention_purchase']:.2f} 元")
        print(f"  - UBI群体总收入: {ubi['total_monthly']:.2f} 元/月 (年收入 {(ubi['total_monthly']*12)/1e4:.2f} 万元)")

        # --- 收支平衡分析 ---
        print("\n--- 2. 各部门收支平衡分析 ---")
        # a. 数字经济
        de_balance = sol['digital_economy_balance_sheet']
        de_costs = de_balance['costs']
        de_rev = de_balance['revenue']
        print("  a. 数字经济 (年化):")
        print(f"     - 总规模: {self.digital_economy_size/1e12:.2f} 万亿元")
        print(f"     - 收入 (显性): {de_rev['total_explicit']/1e8:.0f} 亿元 (高净值消费, UBI消费, 政府投资)")
        print(f"     - 成本: {(self.digital_economy_size - de_costs['gross_profit'])/1e8:.0f} 亿元")
        print(f"     - 毛利润: {de_costs['gross_profit']/1e8:.0f} 亿元 (利润率: {de_costs['gross_profit']/self.digital_economy_size:.1%})")
        print(f"     - 平衡项 (出口/其他): {de_rev['export_or_other']/1e8:.0f} 亿元")

        # b. 政府
        print("  b. 政府财政 (年化):")
        gov_budget = {}
        costs_ratios = self.p['digital_cost_ratios']
        gov_budget['digital_tax_revenue'] = self.digital_economy_size * costs_ratios['tax']
        gov_budget['total_tax_revenue'] = gov_budget['digital_tax_revenue'] * self.p['total_tax_to_digital_tax_ratio']
        total_spending = gov_budget['total_tax_revenue'] * sum(self.p['gov_spending_ratios'].values())
        print(f"     - 总税收: {gov_budget['total_tax_revenue']/1e8:.0f} 亿元")
        print(f"     - 总支出: {total_spending/1e8:.0f} 亿元")
        print(f"     - 财政平衡: {(gov_budget['total_tax_revenue'] - total_spending)/1e8:.0f} 亿元")
        
        # --- 可持续性评估 ---
        print("\n--- 3. 可持续性评估 ---")
        issues = []
        if de_costs['gross_profit'] < 0:
            issues.append(f"数字经济亏损 ({de_costs['gross_profit']/1e8:.0f} 亿元)")
        if de_rev['export_or_other'] < -1e9: #允许少量误差
            issues.append("数字经济内部循环无法维系，需要大量外部输入来平衡")
        if ubi['total_monthly'] < 500:
            issues.append(f"总UBI水平较低 ({ubi['total_monthly']:.0f}元/月)，可能无法维持基本生活")

        if issues:
            for i, issue in enumerate(issues, 1):
                print(f"  ⚠️  问题 {i}: {issue}")
        else:
            print("  ✅ 模型在当前参数下表现出可持续性。")
        
        print("="*80)

def main():
    print("="*80)
    print("场景一：运行基准统一模型")
    print("="*80)
    base_model = UnifiedEconomicModel()
    base_model.generate_report()
    
    print("\n\n" + "="*80)
    print("场景二：高税收、高福利再分配模型")
    print("="*80)
    
    scenario_2_params = {
        # 成本结构调整：税收比例显著提高
        "digital_cost_ratios": {
            "personnel": 0.35,
            "operation": 0.20,
            "attention_purchase": 0.05,
            "depreciation": 0.20,
            "tax": 0.15,  # 税收比例从5%提升到15%
        },
        # 财政调整: 更多资金用于UBI
        "gov_spending_ratios": {
            "base_ubi": 0.8, # 80%的税收用于UBI
            "digital_investment": 0.1,
            "other_services": 0.1,
        },
    }
    
    high_welfare_model = UnifiedEconomicModel(params=scenario_2_params)
    high_welfare_model.generate_report()


if __name__ == "__main__":
    main()
